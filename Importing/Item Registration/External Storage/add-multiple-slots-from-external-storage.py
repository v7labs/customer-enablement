'''
# Script name: add-multiple-slots-from-external-storage.py
# Last edited: 14.11.23

DESCRIPTION
When executed from the command line, this script:
- 1: Registers items from external storage to multiple slots in Darwin

USAGE
python3 add-multiple-slots-from-external-storage.py [-h] api_key team_slug dataset_slug storage_name

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
team_slug: slugified version of the team name
dataset_slug: slugified version of the dataset name
storage_name: Name of the external storage account

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

import requests
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
        'dataset_slug',
        help='slugified version of the dataset name'
    )
    parser.add_argument(
        'storage_name',
        help='Name of the external storage account'
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

def main() -> None:
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    # Define API request headers
    headers = {
     "Content-Type": "application/json",
     "Accept": "application/json",
     "Authorization": f"ApiKey {args.api_key}"
     }
    
    payload = {
     "items": [
          {
               "layout": {
               "slots": ["1", "2"],
               "version": 1,
               "type": "horizontal"
               },
               "path": "/",
               "slots": [
                    {
                         "as_frames": "false",
                         "slot_name": "1",
                         "storage_key": "example-left.jpeg",
                         "file_name": "example-left.jpeg"
                    },
                    {
                         "as_frames": "false",
                         "slot_name": "2",
                         "storage_key": "example-right.jpeg",
                         "file_name": "example-right.jpeg"
                    }
               ],
               "name": "Two Slot Example"
          }
     ],
     "dataset_slug": args.dataset_slug,
     "storage_slug": args.storage_name
     }
    
    response = requests.post(
     f"https://darwin.v7labs.com/api/v2/teams/{args.team_slug}/items/register_existing",
     headers=headers,
     json=payload
     )


if __name__ == '__main__':
    main()

