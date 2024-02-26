"""
# Script name: register_single_rw_file.py
# Last edited: 

DESCRIPTION
When executed from the command line, this script:
- 1: Registers a single file in an S3 bucket in a read/write configuration with a Darwin dataset.

USAGE
python register_single_rw_file.py

For more information on registering items from external storage, see: https://docs.v7labs.com/docs/registering-new-images-or-videos-copy

REQUIRED VARIABLES
Please populate the following variables before executing the script:
- API_KEY: The API key.
- TEAM_SLUG: The team slug.
- DATASET_SLUG: The dataset slug.
- STORAGE_NAME: The storage name.
- STORAGE_KEY: The storage key.
- FILE_NAME: The file name.
"""

import requests
from typing import Dict, Any

# Populate these variables before executing the script
API_KEY = "ApiKey"
TEAM_SLUG = "team-slug"
DATASET_SLUG = "dataset-slug"
STORAGE_NAME = "storage-name"
STORAGE_KEY = "storage-key"
FILE_NAME = "file-name"


def build_headers() -> Dict[str, str]:
    """
    Build the request headers.

    Returns
    -------
    dict
        The headers.
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"ApiKey {API_KEY}",
    }


def build_payload() -> Dict[str, Any]:
    """
    Build the request payload.

    Returns
    -------
    dict
        The payload.
    """
    return {
        "items": [
            {
                "path": "/",
                "as_frames": "false",
                "storage_key": STORAGE_KEY,
                "file_name": FILE_NAME,
                "name": FILE_NAME,
            }
        ],
        "dataset_slug": DATASET_SLUG,
        "storage_slug": STORAGE_NAME,
    }


def send_request():
    """
    Send the registration request and print the response.
    """
    headers = build_headers()
    payload = build_payload()

    response = requests.post(
        f"https://darwin.v7labs.com/api/v2/teams/{TEAM_SLUG}/items/register_existing",
        headers=headers,
        json=payload,
    )

    if response.status_code != 200:
        print("request failed", response.text)
    else:
        print("success")


def main():
    send_request()


if __name__ == "__main__":
    main()
