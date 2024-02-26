"""
Script name: delete_archived_files.py
Last Edited: 26.02.24

DESCRIPTION
This script is used to delete archived files from a dataset in a Darwin team. 
It first fetches the count of archived files in the dataset, warns the user about the number of files about to be deleted, 
and then proceeds to delete the files in batches.

USAGE
To use this script, populate the global variables API_KEY, TEAM_SLUG, DATASET_ID, and RESPONSES_PER_REQUEST with appropriate values.
Then, run the script.

REQUIRED VARIABLES
API_KEY: The API key for authentication with Darwin.
TEAM_SLUG: The slug for your Darwin team.
DATASET_ID: The ID for your Darwin dataset.
RESPONSES_PER_REQUEST: The number of responses per request.

FUNCTIONS
get_archived_count(): Fetches and returns the count of archived files in the dataset.
warn_user(archived_count): Warns the user about the number of files about to be deleted.
delete_files(archived_count): Deletes the archived files in batches.
main(): The main function that calls the other functions in order.
"""

import requests
import json
import sys

# Global variables
API_KEY = "ApiKey"
TEAM_SLUG = "team-slug"
DATASET_ID = 000000
RESPONSES_PER_REQUEST = 500

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"ApiKey {API_KEY}",
}


def get_archived_count():
    counts_url = f"https://darwin.v7labs.com/api/v2/teams/{TEAM_SLUG}/items/general_counts?statuses=archived&dataset_ids={DATASET_ID}"
    return json.loads(requests.get(counts_url, headers=headers).text)["simple_counts"][
        0
    ]["filtered_item_count"]


def warn_user(archived_count):
    if archived_count == 0:
        sys.exit("No archived files in dataset. Please review your dataset and rerun.")
    else:
        continue_warning = input(
            f"===== WARNING =====\n\
You are about to permanently delete {archived_count} files.\n\
To continue, enter 'Yes'. Enter anything else to cancel.\n>>> "
        )
        if continue_warning.lower() != "yes":
            sys.exit(f"Deletion of {archived_count} files cancelled.")


def delete_files(archived_count):
    num_requests = (
        int(archived_count / RESPONSES_PER_REQUEST) + 1
        if archived_count % RESPONSES_PER_REQUEST != 0
        else archived_count / RESPONSES_PER_REQUEST
    )
    print(f"Beginning deletion of {archived_count} files in {num_requests} batches.")

    while archived_count > 0:
        url = f"https://darwin.v7labs.com/api/v2/teams/{TEAM_SLUG}/items?statuses=archived&dataset_ids={DATASET_ID}&page[size]={RESPONSES_PER_REQUEST}"
        response = requests.get(url, headers=headers).json()
        filenames = [x["name"] for x in response["items"]]

        payload = {"filters": {"item_names": filenames, "dataset_ids": [DATASET_ID]}}
        url = f"https://darwin.v7labs.com/api/v2/teams/{TEAM_SLUG}/items"
        response = requests.delete(url, json=payload, headers=headers)
        print(f"Deleting {len(filenames)} file(s)...")
        archived_count -= RESPONSES_PER_REQUEST

    print("Done!")


def main():
    archived_count = get_archived_count()
    warn_user(archived_count)
    delete_files(archived_count)


if __name__ == "__main__":
    main()
