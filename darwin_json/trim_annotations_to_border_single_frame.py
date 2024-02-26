"""
# Script name: trim_annotations_to_border_single_frame.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Trims the annotations of an image to its border
- 2: Outputs a new file with the trimmed annotations

USAGE
python trim_annotations_to_border_single_frame.py [-h] -i INPUT [-o OUTPUT]

REQUIRED ARGUMENTS
-i INPUT, --input INPUT    The input file to be processed

OPTIONAL ARGUMENTS
-o OUTPUT, --output OUTPUT The output file to write the results to
-h, --help                 Print the help message for the function and exit
"""

import json
import os
import argparse
from typing import Dict, Any, Optional, Union, cast, List


class Trimmer:
    def trim(self, filename: str, output_filename: Optional[str]) -> None:
        """
        Trims the annotations of an image to its border and writes the results to a new file.

        Parameters
        ----------
            filename (str): The input file to be processed
            output_filename (str, optional): The output file to write the results to

        Raises
        ------
            ValueError: If no image is found to convert
        """
        with open(filename) as export_file:
            file_content: str = export_file.read()
            export: Dict[str, Any] = json.loads(file_content)

            image: Optional[Dict[str, Union[float, str]]] = export["item"]["slots"]
            if image is None:
                raise ValueError("No image found to convert.")

            max_width: float = cast(float, image[0].get("width"))
            max_height: float = cast(float, image[0].get("height"))
            annotations: List[Dict[str, Any]] = export.get("annotations", [])
            annotations_inside_image: List[Dict[str, Any]] = []
            for annotation in annotations:
                if not self._is_completely_outside_image(
                    annotation, max_width, max_height
                ):
                    annotations_inside_image.append(annotation)

            new_annotations: List[Dict[str, Any]] = []
            for annotation in annotations_inside_image:
                new_annotations.append(
                    self._trim_to_max_values(annotation, max_width, max_height)
                )
            new_export: Dict[str, Any] = export
            new_export["annotations"] = new_annotations

            if output_filename is None:
                old_filename, ext = os.path.splitext(filename)
                output_filename = f"{old_filename}_trimmed{ext}"

            with open(output_filename, "w") as trimmed_file:
                new_content = json.dumps(new_export)
                trimmed_file.write(new_content)

    def _is_completely_outside_image(
        self, annotation: Dict[str, Any], max_width: float, max_height: float
    ) -> bool:
        """
        Checks if an annotation is completely outside the image.

        Parameters
        ----------
            annotation (Dict[str, Any]): The annotation to check
            max_width (float): The maximum width of the image
            max_height (float): The maximum height of the image

        Returns
        -------
            bool: True if the annotation is completely outside the image, False otherwise
        """
        if self._is_bounding_box(annotation):
            bbox: Dict[str, float] = cast(
                Dict[str, float], annotation.get("bounding_box")
            )

            left_x: float = cast(float, bbox.get("x"))
            right_x: float = left_x + cast(float, bbox.get("w"))
            top_y: float = cast(float, bbox.get("y"))
            bottom_y: float = top_y + cast(float, bbox.get("h"))

            return (
                (left_x < 0 and right_x < 0)
                or (left_x > max_width and right_x > max_width)
                or (top_y < 0 and bottom_y < 0)
                or (top_y > max_height and bottom_y > max_height)
            )

        return False

    def _trim_to_max_values(
        self, annotation: Dict[str, Any], max_width: float, max_height: float
    ) -> Dict[str, Any]:
        """
        Trims an annotation to the maximum values of the image.

        Parameters
        ----------
            annotation (Dict[str, Any]): The annotation to trim
            max_width (float): The maximum width of the image
            max_height (float): The maximum height of the image

        Returns
        -------
            Dict[str, Any]: The trimmed annotation
        """
        if self._is_bounding_box(annotation):
            bbox: Dict[str, float] = annotation.get("bounding_box", {})
            trimmed_bbox: Dict[str, float] = self._trim_bounding_box(
                bbox, max_width, max_height
            )
            annotation["bounding_box"] = trimmed_bbox
            if self._is_polygon(annotation):
                polygon: Dict[str, float] = annotation.get("polygon", {})
                trimmed_polygon: Dict[str, float] = self._trim_polygon(
                    polygon, max_width, max_height
                )
                annotation["polygon"] = trimmed_polygon
        return annotation

    def _is_bounding_box(self, annotation: Dict[str, Any]) -> bool:
        """
        Checks if an annotation is a bounding box.

        Parameters
        ----------
            annotation (Dict[str, Any]): The annotation to check

        Returns
        -------
            bool: True if the annotation is a bounding box, False otherwise
        """
        return annotation.get("bounding_box") is not None

    def _is_polygon(self, annotation: Dict[str, Any]) -> bool:
        """
        Checks if an annotation is a polygon.

        Parameters
        ----------
            annotation (Dict[str, Any]): The annotation to check

        Returns
        -------
            bool: True if the annotation is a polygon, False otherwise
        """
        return annotation.get("polygon") is not None

    def _trim_bounding_box(
        self, bbox: Dict[str, float], max_width: float, max_height: float
    ) -> Dict[str, float]:
        """
        Trims a bounding box to the maximum values of the image.

        Parameters
        ----------
            bbox (Dict[str, float]): The bounding box to trim
            max_width (float): The maximum width of the image
            max_height (float): The maximum height of the image

        Returns
        -------
            Dict[str, float]: The trimmed bounding box
        """
        # Trimming logic here...

    def _trim_polygon(
        self, polygon: Dict[str, float], max_width: float, max_height: float
    ) -> Dict[str, float]:
        """
        Trims a polygon to the maximum values of the image.

        Parameters
        ----------
            polygon (Dict[str, float]): The polygon to trim
            max_width (float): The maximum width of the image
            max_height (float): The maximum height of the image

        Returns
        -------
            Dict[str, float]: The trimmed polygon
        """
        # Trimming logic here...


def main():
    parser = argparse.ArgumentParser(
        description="Trim the annotations of an image to its border."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="The input file to be processed"
    )
    parser.add_argument(
        "-o", "--output", help="The output file to write the results to"
    )
    args = parser.parse_args()

    trimmer = Trimmer()
    trimmer.trim(args.input, args.output)


if __name__ == "__main__":
    main()
