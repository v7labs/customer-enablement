"""
# Script name: convert_darwin_json_to_mask.py
# Last edited: 26.02.24

DESCRIPTION
When executed, this script:
- 1: Takes a list of a list of vectorised polygon points and the height and width of the annotation file
- 2: Returns a binary mask of the polygon
"""

import numpy as np
import upolygon as up
from darwin.utils import convert_polygons_to_sequences

# Define the polygon, height, and width here
POLYGON = [[1, 2], [3, 4], [5, 6]]  # Replace with your actual values
HEIGHT = 100  # Replace with your actual value
WIDTH = 100  # Replace with your actual value


def gen_mask(polygon: list, height: int, width: int) -> np.ndarray:
    """
    Generate a binary mask from a polygon.

    Parameters
    ----------
        polygon (list): List of a list of vectorised polygon points
        height (int): Height of the annotation file
        width (int): Width of the annotation file

    Returns
    -------
        mask (np.ndarray): Binary mask of the polygon
    """
    mask = np.zeros((height, width))
    sequences = convert_polygons_to_sequences(polygon)
    up.draw_polygon(mask, sequences, 1)
    return mask


def main():
    mask = gen_mask(POLYGON, HEIGHT, WIDTH)
    print(mask)


if __name__ == "__main__":
    main()
