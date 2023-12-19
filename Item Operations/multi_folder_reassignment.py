'''
# Script name: multi_folder_reassignment.py
# Last edited: 14.11.23

DESCRIPTION
When executed from the command line, this script:
- 1: Reassigns files from multiple folders to the same destination folder in a V7 dataset.

USAGE
python3 multi_folder_reassignment.py [-h] api_key team_slug dataset_id destination_folder

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
team_slug: slugified version of the team name
dataset_id: id of the dataset
destination_folder: Path to destination folder on Darwin


OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

import requests
import json
import sys
import argparse
import re


def get_args() -> argparse.Namespace:
    '''
    Parse and return command line arguments.

    Returns
    -------
        args (argparse.Namespace): API key, output directory and filename
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'api_key',
        help='API key for authentication with Darwin'
    )
    parser.add_argument(
        'team_slug',
        help='slugified version of the team name'
    )
    parser.add_argument(
        'dataset_id',
        help='id of the dataset'
    )
 
    return parser.parse_args()

def validate_api_key(
    api_key: str
    ) -> None:
    '''
    Validates the given API key. Exits if validation fails.

    Parameters
    ----------
        api_key (str): The API key to be validated

    Raises
    ------
        ValueError: If the API key failed validation
    '''
    example_key = "DHMhAWr.BHucps-tKMAi6rWF1xieOpUvNe5WzrHP"
    api_key_regex = re.compile(r'^\w{7}\.\w{32}$')
    assert api_key_regex.match(api_key), f'Expected API key to match the pattern: {example_key}'


def main():
    ''' main():
        Reassigns files from multiple folders to the same destination folder in a V7 dataset.

    '''
    args = get_args()
    validate_api_key(args.api_key)


    folder_paths = [
        "/path/to/folder/1",
        "/path/to/folder/2",
        "...",
        "/path/to/folder/n"
    ]

    url = f"https://darwin.v7labs.com/api/v2/teams/{args.team_slug}/items/path"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {args.api_key}"
     }
    payload = {
        "filters": {
            "item_paths": folder_paths,
            "dataset_ids": args.dataset_ids
        },
        "path": args.destination_folder
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

if __name__ == "__main__":
    main()
