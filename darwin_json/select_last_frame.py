"""
# Script name: select_last_frame.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Splits the source annotation video file into separate files.

USAGE
python select_last_frame.py [-h] --source_path SOURCE_PATH --destination_path DESTINATION_PATH --next_file_name NEXT_FILE_NAME

REQUIRED ARGUMENTS
--source_path SOURCE_PATH       The source path containing your annotation file to be split.
--destination_path DESTINATION_PATH       The destination path for the new annotation file.
--next_file_name NEXT_FILE_NAME       Name of the item this new annotation will be added to.

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
import json
from pathlib import Path
from typing import Dict


def first_key(dict: Dict) -> str:
    """
    Function to return first key of a dictionary. Used to make JSON parsing tidier.

    Parameters
    ----------
    dict: Dict
      source dictionary

    Returns
    -------
    str: first key of the dictionary
    """
    return str(next(iter(dict)))


def last_key(dict: Dict) -> str:
    """
    Function to return last key of a dictionary. Used to make JSON parsing tidier.

    Parameters
    ----------
    dict: Dict
      source dictionary

    Returns
    -------
    str: last key of the dictionary
    """
    return list(dict)[-1]


def main():
    parser = argparse.ArgumentParser(
        description="Splits the source annotation video file into separate files."
    )
    parser.add_argument(
        "--source_path",
        type=str,
        required=True,
        help="The source path containing your annotation file to be split.",
    )
    parser.add_argument(
        "--destination_path",
        type=str,
        required=True,
        help="The destination path for the new annotation file.",
    )
    parser.add_argument(
        "--next_file_name",
        type=str,
        required=True,
        help="Name of the item this new annotation will be added to.",
    )
    args = parser.parse_args()

    source_path = Path(args.source_path)
    destination_path = Path(args.destination_path)
    next_file_name = args.next_file_name

    with open(source_path) as f:
        data = json.load(f)

    # Defining new file name and retrieving last frame value
    if data["version"] == "1.0":
        data["image"]["filename"] = next_file_name
        last_frame = data["image"]["frame_count"] - 1

    else:
        data["item"]["name"] = next_file_name
        last_frame = data["item"]["slots"][0]["frame_count"] - 1

    try:
        annotators = data["annotators"]
    except KeyError:
        pass

    annotations = data["annotations"]

    del data["annotations"]
    try:
        del data["annotators"]
    except KeyError:
        pass

    data["annotations"] = []

    # Based on the selected frame which is converted into its own annotation file
    for anno in annotations:
        temp_anno = {}
        temp_anno["frames"] = {}

        if int(last_key(anno["frames"])) == last_frame:
            temp_anno["frames"]["0"] = anno["frames"][str(last_key(anno["frames"]))]
            data["annotations"].append(temp_anno)

        else:
            continue

        temp_anno["annotators"] = anno["annotators"]
        temp_anno["id"] = anno["id"]
        try:
            temp_anno["interpolate_algorithm"] = anno["interpolate_algorithm"]
            temp_anno["interpolated"] = anno["interpolated"]
        except KeyError:
            temp_anno["interpolate_algorithm"] = "linear-1.1"
            temp_anno["interpolated"] = True
        temp_anno["name"] = anno["name"]
        temp_anno["reviewers"] = anno["reviewers"]

    # Adds Final Annotators Section
    try:
        data["annotators"] = annotators
    except KeyError:
        pass

    # Writing back new file
    with open(destination_path, "w+") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
