"""
# Script name: upload_multiple_dicoms.py
# Last edited: 07.01.24

DESCRIPTION
When executed from the command line, this script:
- Uploads folders of DICOM files in different slots as a single dataset item.
- The files in each folder will be uploaded to a different slot in a natural order (i.e. "A2" < "A10").

USAGE
python upload_multiple_dicoms.py [-h] api_key team_slug dataset_slug

NOTE - The SLOT_NAMES and PATHS variables must be populated before running the script.

REQUIRED ARGUMENTS
api_key: API key for authentication with Darwin
team_slug: Team slug for Darwin
dataset_slug: Dataset slug for Darwin

OPTIONAL ARGUMENTS
-h, --help: Print the help message for the function and exit
"""

import argparse
import requests
import json
import re
from pathlib import Path

SLOT_NAMES = ["example_slot_1", "example_slot_2", "example_slot_3"]

FOLDER_PATHS = [
    Path("example_folder_1"),
    Path("example_folder_2"),
    Path("example_folder_3"),
]


def get_args() -> argparse.Namespace:
    """
    Parse and return command line arguments.

    Returns
    -------
        args (argparse.Namespace): API key, team slug, and dataset slug
    """
    parser = argparse.ArgumentParser(
        description="Uploads folders of DICOM files in different slots as a single dataset item."
    )
    parser.add_argument("api_key", help="API key for authentication with Darwin")
    parser.add_argument("team_slug", help="Team slug for Darwin")
    parser.add_argument("dataset_slug", help="Dataset slug for Darwin")
    return parser.parse_args()


def validate_api_key(api_key: str) -> None:
    """
    Validates the given API key. Exits if validation fails.

    Parameters
    ----------
        api_key (str): The API key to be validated

    Raises
    ------
        ValueError: If the API key failed validation
    """
    example_key = "DHMhAWr.BHucps-tKMAi6rWF1xieOpUvNe5WzrHP"
    api_key_regex = re.compile(r"^.{7}\..{32}$")
    assert api_key_regex.match(
        api_key
    ), f"Expected API key to match the pattern: {example_key}"


def get_files_and_perform_upload(
    api_key: str, team_slug: str, dataset_slug: str
) -> None:
    """
    Uploads folders of DICOM files in different slots as a single dataset item.

    Parameters
    ----------
        api_key (str): API key for authentication with Darwin
        team_slug (str): Team slug for Darwin
        dataset_slug (str): Dataset slug for Darwin
    """
    items, slots = [], []
    filenames, filepaths = [], []
    for path_idx, path in enumerate(FOLDER_PATHS):
        folder_filenames = [
            i.name for i in Path(path).iterdir() if not i.name.startswith(".")
        ]
        folder_filenames.sort()
        human_sort(folder_filenames)
        filenames.append(folder_filenames)
        for item_idx, item in enumerate(folder_filenames):
            filepaths.append(Path(path / item))
            slots.append(
                {
                    "as_frames": False,
                    "file_name": filenames[path_idx][item_idx],
                    "slot_name": SLOT_NAMES[path_idx],
                }
            )
    items.append({"path": "/", "slots": slots, "name": "filename"})

    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/register_upload"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"ApiKey {api_key}",
    }
    payload = {
        "items": items,
        "dataset_slug": dataset_slug,
        "options": {"ignore_dicom_layout": True},
    }

    # Register the files
    response = requests.post(url, json=payload, headers=headers)
    request_response = json.loads(response.text)

    # Define dictionaries mapping filenames to filepaths and upload_ids
    filepath_dict = {}
    for path in filepaths:
        name = path.name
        filepath_dict[name] = path

    upload_id_dict = {}
    for item in request_response["items"]:
        for slot in item["slots"]:
            upload_id_dict[slot["upload_id"]] = filepath_dict[slot["file_name"]]

    # Signing uploads, uploading, and confirming uploads
    for upload_id in upload_id_dict:
        url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/uploads/{upload_id}/sign"
        response = requests.get(url, headers=headers)

        res = json.loads(response.text)
        upload_url = res["upload_url"]
        with open(upload_id_dict[upload_id], "rb") as f:
            data = f.read()
        response = requests.put(url=upload_url, data=data)

        url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/uploads/{upload_id}/confirm"
        payload = {"name": "example_slots"}
        response = requests.post(url, json=payload, headers=headers)


def tryint(s):
    """
    Return an int if possible, or `s` unchanged.
    """
    try:
        return int(s)
    except ValueError:
        return s


def alphanum_key(s):
    """
    Turn a string into a list of string and number chunks.

    >>> alphanum_key("z23a")
    ["z", 23, "a"]

    """
    return [tryint(c) for c in re.split("([0-9]+)", s)]


def human_sort(list_to_sort):
    """
    Sort a list in the way that humans expect.
    """
    list_to_sort.sort(key=alphanum_key)


def main() -> None:
    """
    Top level function to execute sub-functions.
    """
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)
    get_files_and_perform_upload(args.api_key, args.team_slug, args.dataset_slug)

    # Call the rest of your functions here


if __name__ == "__main__":
    main()
