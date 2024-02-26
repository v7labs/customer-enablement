"""
# Script name: iou_calculator.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script takes two polygons and calculates the Intersection over Union (IoU) value.

USAGE
python iou_calculator.py

REQUIRED ARGUMENTS
None

OPTIONAL ARGUMENTS
-h, --help           Print the help message for the function and exit
"""

import numpy as np
import upolygon as up
import iou_utils as iou

from darwin.utils import convert_polygons_to_sequences
from typing import List, Dict

# Define the polygons, height and width
polygon1 = [
    {"x": 61.0, "y": 132.0},
    {"x": 56.0, "y": 137.0},
    {"x": 56.0, "y": 139.0},
    {"x": 55.0, "y": 140.0},
]
polygon2 = [
    {"x": 61.0, "y": 132.0},
    {"x": 56.0, "y": 137.0},
    {"x": 56.0, "y": 139.0},
    {"x": 55.0, "y": 140.0},
]
height = 277
width = 640


def gen_mask(polygon: List[Dict[str, float]], height: int, width: int) -> np.ndarray:
    """
    Takes a list of vectorised polygon points and returns a binary mask

    Parameters
    ----------
        polygon (List[Dict[str, float]]): The polygon as a list of dictionaries with 'x' and 'y' keys.
        height (int): The height of the image.
        width (int): The width of the image.

    Returns
    -------
        mask (np.ndarray): The binary mask of the polygon.
    """
    mask = np.zeros((height, width))
    sequences = convert_polygons_to_sequences(polygon)
    up.draw_polygon(mask, sequences, 1)
    return mask


def main():
    mask_1 = gen_mask(polygon1, height, width)
    mask_2 = gen_mask(polygon2, height, width)

    Intersection = iou.Array_AND(mask_1, mask_2)[1]
    Overlap = iou.Array_OR(mask_1, mask_2)[1]

    IOU_value = Intersection / Overlap
    print(IOU_value)
    return IOU_value


if __name__ == "__main__":
    main()
