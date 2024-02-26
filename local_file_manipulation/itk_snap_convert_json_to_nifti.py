"""
This script converts JSON files, which contain medical imaging data and metadata, into NIFTI format. The JSON files are expected to be in a specific format, known as Darwin JSON, which includes information about the image dimensions, pixel dimensions, affine transformations, and annotations.

The script provides several functions to load the JSON data, decode the run-length encoding (RLE) used for the image data, process the metadata, and apply the affine transformations. The processed data is then saved as a NIFTI file, which is a common format for storing medical imaging data.

The script also generates a label file for use with ITK-SNAP, a software application used to segment structures in 3D medical images. This label file includes information about the different annotations in the image, such as their color and visibility.

The main function, `convert`, takes an input directory and an output directory as arguments. It processes all JSON files in the input directory and saves the resulting NIFTI files in the output directory.
"""

import json
import numpy as np
import os
import ast
import glob
import fire
from typing import Dict, Tuple
import nibabel as nib
from nibabel.orientations import io_orientation, ornt_transform

from matplotlib import colormaps


def load_json(json_path):
    """Loads JSON data from a given path."""
    with open(json_path) as file:
        data = json.load(file)
    return data


def decode_rle(rle_data, width, height, mapping):
    """Decodes run-length encoding (RLE) data into a mask array."""
    total_pixels = width * height
    mask = np.zeros(total_pixels, dtype=np.uint8)
    pos = 0
    for i in range(0, len(rle_data), 2):
        value = mapping[rle_data[i]]
        length = rle_data[i + 1]
        mask[pos : pos + length] = value
        pos += length
    return mask.reshape(height, width)


def process_metadata(metadata: Dict) -> Tuple:
    """Processes metadata for volume dimensions, pixel dimensions, and affine transformations."""
    volume_dims = metadata.get("shape")
    pixdim = metadata.get("pixdim")
    affine = process_affine(metadata.get("affine"))
    original_affine = process_affine(metadata.get("original_affine"))

    if isinstance(pixdim, str):
        pixdim = ast.literal_eval(pixdim)
        if isinstance(pixdim, (tuple, list)):
            if len(pixdim) == 4:
                pixdim = pixdim[1:]
            if len(pixdim) != 3:
                pixdim = None
        else:
            pixdim = None
    if isinstance(volume_dims, list) and volume_dims:
        if volume_dims[0] == 1:  # Remove first singleton dimension
            volume_dims = volume_dims[1:]
    return volume_dims, pixdim, affine, original_affine


def process_affine(affine):
    """Processes the affine transformation matrix."""
    if isinstance(affine, str):
        affine = np.squeeze(
            np.array([ast.literal_eval(line) for line in affine.split("\n")])
        )
    elif isinstance(affine, list):
        affine = np.array(affine).astype(float)
    else:
        return
    if isinstance(affine, np.ndarray):
        return affine


def process_and_flip_image(json_path, nifti_path_output):
    """Processes Darwin JSON data, applies the affine transform, and saves as a NIFTI file."""
    data = load_json(json_path)
    masks = []

    slot = data["item"]["slots"][0]
    width, height = slot["width"], slot["height"]
    zeroes = np.zeros((height, width), dtype=np.uint8)
    volume_dims, pixdims, affine, original_affine = process_metadata(slot["metadata"])
    global_mapping = {
        annotation["id"]: i + 1 for i, annotation in enumerate(data["annotations"])
    }
    global_mapping_names = {
        i + 1: annotation["name"] for i, annotation in enumerate(data["annotations"])
    }

    for annotation in data["annotations"]:
        if annotation["name"] == "__raster_layer__":
            for frame_number in range(int(slot["frame_count"])):
                frame = str(frame_number)
                if frame in annotation["frames"]:
                    frame_data = annotation["frames"][frame]
                    if "raster_layer" in frame_data:
                        raster_layer = frame_data["raster_layer"]
                        dense_rle = raster_layer["dense_rle"]
                        mask_annotation_ids_mapping = raster_layer[
                            "mask_annotation_ids_mapping"
                        ]
                        frame_mapping = {
                            v: global_mapping[k]
                            for k, v in mask_annotation_ids_mapping.items()
                        } | {0: 0}
                        mask_2d = decode_rle(dense_rle, width, height, frame_mapping)
                        masks.append(mask_2d)
                else:
                    masks.append(zeroes)

    if not masks:
        print(f"No masks found for {json_path}.")
        return None

    mask_3d = np.stack(masks)
    mask_3d = np.transpose(mask_3d, (2, 1, 0))
    img = nib.Nifti1Image(
        dataobj=np.flip(mask_3d, (0, 1, 2)).astype(np.int16), affine=affine
    )

    if original_affine is not None:
        orig_ornt = io_orientation(original_affine)
        img_ornt = io_orientation(affine)
        from_canonical = ornt_transform(img_ornt, orig_ornt)
        img = img.as_reoriented(from_canonical)

    nib.save(img=img, filename=nifti_path_output)

    # write a itk snap label file
    label_file_path = nifti_path_output + ".label"
    #    IDX:   Zero-based index
    #    -R-:   Red color component (0..255)
    #    -G-:   Green color component (0..255)
    #    -B-:   Blue color component (0..255)
    #    -A-:   Label transparency (0.00 .. 1.00)
    #    VIS:   Label visibility (0 or 1)
    #    IDX:   Label mesh visibility (0 or 1)
    #  LABEL:   Label description
    colormap = colormaps.get("Set1")
    with open(label_file_path, "w") as label_file:
        for id, i in global_mapping.items():
            color = colormap.colors[i]
            label_file.write(
                f'{i} {int(color[0] * 255)} {int(color[1] * 255)} {int(color[2] * 255)} 1 1 1 "{global_mapping_names[i]}"\n'
            )


def convert(input_dir="./input", output_dir="./output"):
    """Converts JSON files in the input directory to NIFTI format in the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    for json_path in glob.glob(os.path.join(input_dir, "*.json")):
        base_name = os.path.basename(json_path)
        file_name = os.path.splitext(base_name)[0]
        file_name_nii = file_name.replace(".nii", "")
        nifti_path_output = os.path.join(output_dir, f"itk_snap_{file_name_nii}.nii")
        process_and_flip_image(json_path, nifti_path_output)


if __name__ == "__main__":
    fire.Fire()
