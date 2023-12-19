'''
# Script name: add-instructions-api.py
# Last edited: 27.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Adds instructions to specific dataset

USAGE
python3 add-instructions-api.py [-h] api_key dataset_id dataset_name 

REQUIRED ARGUMENTS
api_key: API key for authentication with Darwin
dataset_id: ID of the dataset to add instructions to
dataset_name: Name of the dataset to add instructions to

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
        'dataset_id',
        help='ID of the dataset to add instructions to'
    )
    parser.add_argument(
        'dataset_name',
        help='Name of the dataset to add instructions to'
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

    url = f"https://darwin.v7labs.com/api/datasets/{args.dataset_id}"

    #Note: this will overwrite previous instructions
    payload = {
        "instructions": "<p>Even text.<br><strong>Example bold text.</p>",
        "name": args.dataset_name,
        "pdf_fit_page":True
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {args.api_key}"
    }

    response = requests.put(url, json=payload, headers=headers)

    print(response.text)

if __name__ == '__main__':
    main()