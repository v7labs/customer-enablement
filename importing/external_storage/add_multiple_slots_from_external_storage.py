"""
# Script name: add_multiple_slots_from_external_storage.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Adds multiple slots from external storage as a dataset item

USAGE
python add_multiple_slots_from_external_storage.py [-h] --api_key API_KEY --team_slug TEAM_SLUG --dataset_slug DATASET_SLUG --storage_name STORAGE_NAME

For more information on registering items from external storage, see: https://docs.v7labs.com/docs/registering-new-images-or-videos-copy

REQUIRED ARGUMENTS
--api_key API_KEY
--team_slug TEAM_SLUG
--dataset_slug DATASET_SLUG
--storage_name STORAGE_NAME

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
import requests


def validate_args(args: argparse.Namespace) -> None:
    """
    Validate the command line arguments

    Parameters
    ----------
        args (argparse.Namespace): The command line arguments

    Raises
    ------
        ValueError: If any of the arguments are invalid
    """
    # Add your validation logic here


def add_slots(
    api_key: str, team_slug: str, dataset_slug: str, storage_name: str
) -> None:
    """
    Add multiple slots from external storage to a dataset

    Parameters
    ----------
        api_key (str): The API key
        team_slug (str): The team slug
        dataset_slug (str): The dataset slug
        storage_name (str): The storage name
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"ApiKey {api_key}",
    }

    payload = {
        "items": [
            {
                "layout": {"slots": ["1", "2"], "version": 1, "type": "horizontal"},
                "path": "/",
                "slots": [
                    {
                        "as_frames": "false",
                        "slot_name": "1",
                        "storage_key": "example-left.jpeg",
                        "file_name": "example-left.jpeg",
                    },
                    {
                        "as_frames": "false",
                        "slot_name": "2",
                        "storage_key": "example-right.jpeg",
                        "file_name": "example-right.jpeg",
                    },
                ],
                "name": "Two Slot Example",
            }
        ],
        "dataset_slug": dataset_slug,
        "storage_slug": storage_name,
    }

    response = requests.post(
        f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/register_existing",
        headers=headers,
        json=payload,
    )

    if response.status_code != 200:
        print("request failed", response.text)
    else:
        print("success")


def main() -> None:
    """
    The main function
    """
    parser = argparse.ArgumentParser(
        description="Add multiple slots from external storage to a dataset"
    )
    parser.add_argument("--api_key", required=True, help="The API key")
    parser.add_argument("--team_slug", required=True, help="The team slug")
    parser.add_argument("--dataset_slug", required=True, help="The dataset slug")
    parser.add_argument("--storage_name", required=True, help="The storage name")

    args = parser.parse_args()

    validate_args(args)

    add_slots(args.api_key, args.team_slug, args.dataset_slug, args.storage_name)


if __name__ == "__main__":
    main()
