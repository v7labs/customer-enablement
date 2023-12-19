'''
# Script name: revoke-access.py
# Last edited: 21.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Revokes access of specific user from Darwin team

USAGE
python3 revoke-access.py [-h] api_key user_id

REQUIRED ARGUMENTS
api_key: API key for authentication with Darwin
user_id: ID of specific user

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

import requests
import logging
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
        'user_id',
        help='ID of specific user'
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

#Can retrieve the user_id from the id field when querying memberships


def main() -> None:
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    # Define API request headers
    headers = {
        'accept': 'application/json',
        'Authorization': f'ApiKey {args.api_key}'
    }

    url = f"https://darwin.v7labs.com/api/memberships/{args.user_id}"

    headers = {
        "accept": "application/json",
        "Authorization": f"ApiKey {args.api_key}"
    }

    # Delete the specific user 
    response = requests.delete(url, headers=headers)

    if response.ok:
        logging.info(f"User: {args.user_id} has been removed from your V7 team")
    else:
        logging.error(f"Error removing team member {args.user_id}")   

if __name__ == '__main__':
    main()