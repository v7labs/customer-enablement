"""
# Script name: register_single_ro_file.py
# Last edited: 

DESCRIPTION
When executed from the command line, this script:
- Registers a single file in an external storage location in a read-only configuration with a Darwin dataset.

USAGE
python register_single_ro_file.py [-h] ...

For more information on registering items from external storage, see: https://docs.v7labs.com/docs/registering-new-images-or-videos-copy

REQUIRED ARGUMENTS
api_key, team_slug

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit

Before running the script, populate the following global variables:
- dataset_slug
- storage_name
- storage_key
- file_name
- storage_thumbnail_key
- width
- height
"""

import argparse
import requests

# Populate these variables before running the script
DATASET_SLUG = "dataset-slug"
STORAGE_NAME = "storage-name"
STORAGE_KEY = "storage-key"
FILE_NAME = "filename"
STORAGE_THUMBNAIL_KEY = "storage-thumbnail-key"
WIDTH = 0000
HEIGHT = 0000


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Register a single file in an external storage location in a read-only configuration with a Darwin dataset."
    )
    parser.add_argument("api_key", type=str, help="API key")
    parser.add_argument("team_slug", type=str, help="Team slug")
    return parser.parse_args()


def register_file(api_key: str, team_slug: str) -> None:
    """Register a file in an external storage location.

    Parameters:
        api_key (str): API key.
        team_slug (str): Team slug.

    Raises:
        Exception: If the request fails.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"ApiKey {api_key}",
    }

    payload = {
        "items": [
            {
                "path": "/",
                "storage_key": STORAGE_KEY,
                "storage_thumbnail_key": STORAGE_THUMBNAIL_KEY,
                "width": WIDTH,
                "height": HEIGHT,
                "file_name": FILE_NAME,
                "type": "image",
                "name": FILE_NAME,
            }
        ],
        "storage_slug": STORAGE_NAME,
        "dataset_slug": DATASET_SLUG,
    }

    response = requests.post(
        f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/register_existing_readonly",
        headers=headers,
        json=payload,
    )

    if response.status_code != 200:
        raise Exception("Request failed", response.text)
    else:
        print("Success")


def main() -> None:
    """Main function."""
    args = parse_arguments()
    register_file(args.api_key, args.team_slug)


if __name__ == "__main__":
    main()
