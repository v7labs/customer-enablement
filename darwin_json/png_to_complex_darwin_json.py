"""
# Script name: png_to_complex_darwin_json.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Converts PNG to Darwin JSON complex polygon paths

USAGE
python png_to_complex_darwin_json.py [-h] --filename FILENAME

REQUIRED ARGUMENTS
--filename FILENAME     The path to the PNG file to be converted

OPTIONAL ARGUMENTS
-h, --help              Print the help message for the function and exit
"""

import argparse
from pathlib import Path
import numpy as np
from upolygon import find_contours
from PIL import Image


def validate_file(filename: str) -> Path:
    """
    Validates the provided filename and returns a Path object.

    Parameters
    ----------
        filename (str): The path to the PNG file to be converted

    Raises
    ------
        ValueError: If the file does not exist or is not a PNG file

    Returns
    -------
        filepath (Path): The validated file path
    """
    filepath = Path(filename)
    if not filepath.exists():
        raise ValueError(f"The file {filename} does not exist.")
    if filepath.suffix.lower() != ".png":
        raise ValueError(f"The file {filename} is not a PNG file.")
    return filepath


def convert_png_to_darwin_json(filename: str) -> list:
    """
    Converts PNG to Darwin JSON complex polygon paths

    Parameters
    ----------
        filename (str): The path to the PNG file to be converted

    Returns
    -------
        paths (list): The list of paths in Darwin JSON format
    """
    masked_image = Image.open(filename).convert("L")

    mask = np.array(masked_image)
    mask[mask > 0] = 1

    _labels, external, _internal = find_contours(mask)

    paths = []
    for external_path in external:
        new_path = []
        # skip paths with less than 2 points
        if len(external_path) // 2 <= 2:
            continue
        points = iter(external_path)
        while True:
            try:
                x, y = next(points), next(points)
                new_path.append({"x": x, "y": y})
            except StopIteration:
                break
        paths.append(new_path)

    for internal_path in _internal:
        new_path = []
        # skip paths with less than 2 points
        if len(internal_path) // 2 <= 2:
            continue
        points = iter(internal_path)
        while True:
            try:
                x, y = next(points), next(points)
                new_path.append({"x": x, "y": y})
            except StopIteration:
                break
        paths.append(new_path)

    return paths


def main():
    parser = argparse.ArgumentParser(
        description="Converts PNG to Darwin JSON complex polygon paths"
    )
    parser.add_argument(
        "--filename", required=True, help="The path to the PNG file to be converted"
    )
    args = parser.parse_args()

    filename = validate_file(args.filename)
    paths = convert_png_to_darwin_json(filename)

    print(paths)


if __name__ == "__main__":
    main()
