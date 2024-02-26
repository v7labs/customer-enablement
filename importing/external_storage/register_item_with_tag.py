"""
Script Name: register_item_with_tag.py

This script registers an item with a tag to a dataset in a specified storage on Darwin.
It requires the following command line arguments: api_key, team_slug, dataset_slug, and storage_name.

Global variables for item details are defined at the top of the script and used in the payload for the API request.

Usage:
python register_item_with_tag.py --api_key <API_KEY> --team_slug <TEAM_SLUG> --dataset_slug <DATASET_SLUG> --storage_name <STORAGE_NAME>

For more information on registering items from external storage, see: https://docs.v7labs.com/docs/registering-new-images-or-videos-copy
"""

import argparse
import requests

# Global variables
ITEM_PATH = "/"
ITEM_AS_FRAMES = "false"
ITEM_STORAGE_KEY = "seals2.mp4"
ITEM_FPS = 10
ITEM_TYPE = "video"
ITEM_TAGS = {
    "ExampleTagClass": "Example Text Subannotation",
    "ExampleTagClass2": "More Example Text",
}
ITEM_NAME = "seals2.mp4"


def register_item_with_tag(
    api_key: str, team_slug: str, dataset_slug: str, storage_name: str
) -> None:
    """
    Registers an item with a tag to a dataset in a specified storage on Darwin.

    Parameters
    ----------
        api_key (str): The API key.
        team_slug (str): The team slug.
        dataset_slug (str): The dataset slug.
        storage_name (str): The storage name.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"ApiKey {api_key}",
    }

    payload = {
        "items": [
            {
                "path": ITEM_PATH,
                "as_frames": ITEM_AS_FRAMES,
                "storage_key": ITEM_STORAGE_KEY,
                "fps": ITEM_FPS,
                "type": ITEM_TYPE,
                "tags": ITEM_TAGS,
                "name": ITEM_NAME,
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
    The main function that parses the command line arguments and calls the register_item_with_tag function.
    """
    parser = argparse.ArgumentParser(
        description="Registers an item with a tag to a dataset in a specified storage on Darwin."
    )
    parser.add_argument("--api_key", required=True, help="The API key.")
    parser.add_argument("--team_slug", required=True, help="The team slug.")
    parser.add_argument("--dataset_slug", required=True, help="The dataset slug.")
    parser.add_argument("--storage_name", required=True, help="The storage name.")
    args = parser.parse_args()

    register_item_with_tag(
        args.api_key, args.team_slug, args.dataset_slug, args.storage_name
    )


if __name__ == "__main__":
    main()
