'''
# Script name: register_single_rw_file.py
# Last edited: 14.11.23

DESCRIPTION
When executed from the command line, this script:
- 1: Registers single item from external storage with read only access in Darwin

USAGE
python3 register_single_rw_file.py [-h] api_key team_slug dataset_slug storage_name storage_key file_name

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
team_slug: slugified version of the team name
dataset_slug: slugified version of the dataset name
storage_name: Name of the external storage account
storage_key: Path to file in your external storage
file_name: The name of the file in the external storage


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
    parser.add_argument(
        'storage_key',
        help='Path to file in your external storage'
    )
    parser.add_argument(
        'file_name',
        help='The name of the file in the external storage'
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
    ''' main()
        Registers a single file from external storage in a read-write configuration with a Darwin dataset.

        Note that the bucket first has to be linked to your V7 team as per the our guidelines:
        https://docs.v7labs.com/docs/aws-s3-configuration

        
    '''
    args = get_args()
    validate_api_key(args.api_key)
    
    headers = {
          "Content-Type": "application/json",
          "Accept": "application/json",
          "Authorization": f"ApiKey {args.api_key}"
     }
    
    payload = {
          "items": [
               {
                    "path": "/",
                    "slots": [
                         {
                              "as_frames": "false",
                              "slot_name": "1",
                              "storage_key": args.storage_key,
                              "file_name": args.file_name
                         }
                    ],
                    "name": args.file_name
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


if __name__ == "__main__":
    main()
