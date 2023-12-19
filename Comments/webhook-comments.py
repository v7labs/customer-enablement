'''
# Script name: webhook-comments.py
# Last edited: 21.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Return comments from webhook responses

USAGE
python3 webhook-comments.py [-h] api_key folder_path 

REQUIRED ARGUMENTS
api_key: API key for authentication with Darwin
folder_path: Path to folder containing files with comments to upload

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

# Modules
import os
import requests
import json
from pathlib import Path
from datetime import datetime
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
        'folder_path',
        help='Path to folder containing files with comments to upload'
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

    # folder_path = "<your-folder-path-where-webhooks-are-stored>"
    folder_path = args.folder_path

    webhook_dict = {}
    for root, dirs, files in os.walk(folder_path):
        for ix, file in enumerate(files):
            f = open(f"{folder_path}/{file}")
            webhook_body = json.load(f)
            webhook_dict[webhook_body['item']['source_info']['item_id']] = webhook_body['item']\
                                                                            ['source_info']['team']['slug']
            f.close

    # Define the header fields for the endpoint
    headers = {
        "accept": "application/json",
        "Authorization": f"ApiKey {args.api_key}"
    }

    comments_list = [] # Initialise empty comments_list

    # Loop through the webhook items from the response to obtain the comments
    for d_id, team_slug in webhook_dict.items():
        url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/{d_id}/comment_threads"
        res = requests.get(url, headers=headers)
        print(f"fetch thread: {'Success' if res.status_code == 200 else 'Failed'}")
        if res.status_code == 200:
            for thread in json.loads(res.text):
                thread_id = thread['first_comment']['comment_thread_id']
                url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/{d_id}/comment_threads/" \
                    f"{thread_id}/comments"
                response = requests.get(url, headers=headers)
                print(f"list comments: {'Success' if res.status_code == 200 else 'Failed'}")
                comments_list.append(json.loads(response.text))
                
    # Dumps the comments from the webhook response into a file
    with open(f"./darwin comments {datetime.now().strftime('%d-%m-%Y %Hh%Mm')}.json", 'w') as f:
        f.write(json.dumps(comments_list, indent=2))

if __name__ == '__main__':
    main()