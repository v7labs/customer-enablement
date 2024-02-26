"""
# Script name: remove_blue_from_images.py
# Last edited: 07.01.24

DESCRIPTION
When executed from the command line, this script:
- 1: Removes blue pixels from all .jpeg and .png images in a given source folder
- 2: Saves the new images in a specified target folder

USAGE
python3 remove_blue_from_images.py [-h] source_folder target_folder

REQUIRED ARGUMENTS
source_folder: Path to the source folder containing the images
target_folder: Path to the target folder where the new images will be saved

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
from pathlib import Path
from PIL import Image


def get_args() -> argparse.Namespace:
    """
    Parse and return command line arguments.

    Returns
    -------
        args (argparse.Namespace): Source folder and target folder paths
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_folder",
        type=Path,
        help="Path to the source folder containing the images",
    )
    parser.add_argument(
        "target_folder",
        type=Path,
        help="Path to the target folder where the new images will be saved",
    )
    return parser.parse_args()


def validate_arguments(source_folder: Path, target_folder: Path) -> None:
    """
    Validates the given source and target folder paths.
    If the source folder does not exist, raises an error.
    If the target folder does not exist, it is created.

    Parameters
    ----------
        source_folder (Path): The source folder path
        target_folder (Path): The target folder path

    Raises
    ------
        ValueError: If the source folder does not exist
    """
    if not source_folder.is_dir():
        raise ValueError(f"Source folder {source_folder} does not exist.")
    if not target_folder.is_dir():
        target_folder.mkdir(parents=True, exist_ok=True)
        print(f"Target directory {target_folder} created.")


def remove_color(
    source_img: Path,
    target_folder: Path,
    name: str,
    red_ratio: float = 1.5,
    green_ratio: float = 1.5,
) -> None:
    """
    Generates new image in target folder with blue pixels removed

    Parameters
    ----------
    source_img (Path): Path to file in local directory
    target_folder (Path): Path to folder in local directory where new images will be saved
    red_ratio (float): Float that determines cutoff as a ratio of blue to red RGB values
    green_ratio (float): Float that determines cutoff as a ratio of blue to green RGB values
    """
    image = Image.open(source_img)
    image_data = image.load()
    height, width = image.size

    for loop1 in range(height):
        for loop2 in range(width):
            r, g, b = image_data[loop1, loop2]
            if (
                image_data[loop1, loop2][2] > green_ratio * image_data[loop1, loop2][1]
                and image_data[loop1, loop2][2]
                > red_ratio * image_data[loop1, loop2][0]
            ):
                image_data[loop1, loop2] = 0, 0, 0

    target = target_folder / name
    image.save(target)


def main() -> None:
    """
    Top level function to execute sub-functions
    """
    # Parse and validate command line arguments
    args = get_args()
    validate_arguments(args.source_folder, args.target_folder)

    # Process each image in the source folder
    for file in args.source_folder.glob("*"):
        if file.suffix in (".jpeg", ".jpg", ".png"):
            remove_color(file, args.target_folder, file.name)


if __name__ == "__main__":
    main()
