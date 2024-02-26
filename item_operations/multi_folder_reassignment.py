"""
This script reassigns files from multiple source folders to a single destination folder in a V7 dataset.

The source folders and destination folder are specified by the global variables FOLDER_PATHS and DESTINATION_FOLDER.
The script constructs a payload with these paths and sends a POST request to the V7 API to reassign the files.

The API response is printed to the console.

Global Variables
----------------
API_KEY : str
    The API key for authentication with Darwin.
TEAM_SLUG : str
    The team slug for Darwin.
DATASET_IDS : list
    List of dataset IDs as integers.
DESTINATION_FOLDER : str
    Path to the destination folder.
FOLDER_PATHS : list
    List of paths to the source folders.

Functions
---------
reassign_files()
    Reassigns files from multiple source folders to a single destination folder in a V7 dataset.
main()
    Calls the reassign_files function to reassign files from multiple source folders to a single destination folder in a V7 dataset.

Usage
-----
Populate the global variables and run the script.
"""

import requests

# Global variables
API_KEY = "ApiKey"
TEAM_SLUG = "team-slug"
DATASET_IDS = []  # List of datsetIDs as integers
DESTINATION_FOLDER = "/"  # Path to destination folder
FOLDER_PATHS = ["/path/to/folder/1", "/path/to/folder/2", "...", "/path/to/folder/n"]

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"ApiKey {API_KEY}",
}


def reassign_files():
    url = f"https://darwin.v7labs.com/api/v2/teams/{TEAM_SLUG}/items/path"
    payload = {
        "filters": {"item_paths": FOLDER_PATHS, "dataset_ids": DATASET_IDS},
        "path": DESTINATION_FOLDER,
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)


def main():
    reassign_files()


if __name__ == "__main__":
    main()
