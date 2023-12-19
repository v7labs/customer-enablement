'''
# Script name: delete_archived_files.py
# Last edited: 14.11.23

DESCRIPTION
When executed from the command line, this script:
- 1: Deletes all archived files in the specified dataset

USAGE
python3 delete_archived_files.py [-h] api_key team_slug dataset_id 

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
team_slug: slugified version of the team name
dataset_id: id of the dataset



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
    '''main():
       Lists and deletes archived files in a dataset using pagination.

       This is useful when requests time out due to a large number of files returned in a request.

       === WARNING ===
       This script will permanently delete archived files.
       Deleted files  and teir respsective annotations will not be recoverable.

    '''
    args = get_args()
    validate_api_key(args.api_key)


    responses_per_request = 500
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {args.api_key}"
    }

    # 1: Get item counts
    counts_url = f"https://darwin.v7labs.com/api/v2/teams/{args.team_slug}/items/general_counts?statuses=archived&dataset_ids={args.dataset_id}"
    archived_count = json.loads(requests.get(counts_url, headers=headers).text)["simple_counts"][0]["filtered_item_count"]

    # Warn user with an opportunity to cancel
    if archived_count == 0:
        sys.exit("No archived files in dataset. Please review your dataset and rerun.")
    else:
        continue_warning = input(f"===== WARNING =====\n\
You are about to permanently delete {archived_count} files.\n\
To continue, enter 'Yes'. Enter anything else to cancel.\n>>> ")
        if continue_warning.lower() != "yes":
            sys.exit(f"Deletion of {archived_count} files cancelled.")

    # 2: List and delete files in a paginated fashion
    if archived_count % responses_per_request == 0:
        num_requests = archived_count / responses_per_request
    else:
        num_requests = int(archived_count / responses_per_request) + 1
    print(f"Beginning deletion of {archived_count} files in {num_requests} batches.")

    while archived_count > 0:

        # List responses_per_request items
        url = f"https://darwin.v7labs.com/api/v2/teams/{args.team_slug}/items?statuses=archived&dataset_ids={args.dataset_id}&page[size]={responses_per_request}"
        response = requests.get(url, headers=headers).json()
        filenames = [x["name"] for x in response["items"]]
        
        # Send a request to delete these items
        payload = {
            "filters": {
                "item_names": filenames,
                "dataset_ids": [args.dataset_id]
            }
        }
        url = f"https://darwin.v7labs.com/api/v2/teams/{args.team_slug}/items"
        response = requests.delete(url, json=payload, headers=headers)
        print(f"Deleting {len(filenames)} file(s)...")
        archived_count -= responses_per_request

    print("Done!")

if __name__ == "__main__":
    main()
