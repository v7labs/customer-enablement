"""
This script converts JSON files into NIfTI format using the SimpleITK library. 

The JSON files are expected to contain run-length encoded (RLE) data representing 2D masks. These masks are then stacked to form a 3D image. 

The script also provides functionality to flip the orientation of the resulting NIfTI image. 

The main function 'convert' takes an input directory containing JSON files and an output directory for the NIfTI files. If the output directory does not exist, it is created.

Usage: python converting_json_to_nifti_itk_snap.py --input_dir=<input_directory> --output_dir=<output_directory>
"""

import json
import numpy as np
import SimpleITK as sitk
import os
import glob
import fire


def load_json(json_path):
    # Function to load JSON data from a given path
    with open(json_path) as file:
        data = json.load(file)
    return data


def decode_rle(rle_data, width, height):
    # Function to decode run-length encoding (RLE) data into a mask array
    total_pixels = width * height
    mask = np.zeros(total_pixels, dtype=np.uint8)
    pos = 0
    for i in range(0, len(rle_data), 2):
        value = rle_data[i]
        length = rle_data[i + 1]
        mask[pos : pos + length] = value
        pos += length
    return mask.reshape(height, width)


def process_and_flip_image(json_path, nifti_path_output):
    # Process JSON data and flip the image
    data = load_json(json_path)
    masks = []

    # Extract width and height from the first slot of JSON data
    width = data["item"]["slots"][0]["width"]
    height = data["item"]["slots"][0]["height"]
    zeroes = np.zeros((height, width), dtype=np.uint8)

    # Process each annotation and frame in JSON
    for annotation in data["annotations"]:
        if annotation["name"] == "__raster_layer__":
            for frame_number in range(int(data["item"]["slots"][0]["frame_count"])):
                frame = str(frame_number)
                if frame in annotation["frames"]:
                    frame_data = annotation["frames"][frame]
                    if "raster_layer" in frame_data:
                        raster_layer = frame_data["raster_layer"]
                        dense_rle = raster_layer["dense_rle"]
                        mask_2d = decode_rle(dense_rle, width, height)
                        masks.append(mask_2d)
                else:
                    masks.append(zeroes)

    if not masks:
        print(f"No masks were found for {json_path}.")
        return None

    # Convert list of 2D masks into a 3D image and flip its orientation
    mask_3d = np.stack(masks)
    sitk_image = sitk.GetImageFromArray(mask_3d)
    original_direction = list(sitk_image.GetDirection())
    # Flip the image along the I-S axis
    # original_direction[6] = -original_direction[6]
    # original_direction[7] = -original_direction[7]
    # original_direction[8] = -original_direction[8]
    sitk_image.SetDirection(tuple(original_direction))
    sitk.WriteImage(sitk_image, nifti_path_output)


# Loop through all JSON files and process each
def convert(input_dir="./input", output_dir="./output"):
    os.makedirs(output_dir, exist_ok=True)
    for json_path in glob.glob(os.path.join(input_dir, "*.json")):
        base_name = os.path.basename(json_path)  # Extract file name
        file_name = os.path.splitext(base_name)[0]  # Remove file extension
        file_name_nii = file_name.replace(".nii", "")  # Adjust file name for output

        # Set output file path and process each JSON file
        nifti_path_output = os.path.join(output_dir, f"itk_snap_{file_name_nii}.nii")
        process_and_flip_image(json_path, nifti_path_output)


if __name__ == "__main__":
    fire.Fire()
