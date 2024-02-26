"""
# Script name: sampling.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Skips the review stage for a percentage of items

USAGE
python sampling.py [-h] ...

REQUIRED ARGUMENTS [if any]

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
from numpy import random
import requests
from typing import Dict


def parse_arguments() -> argparse.Namespace:
    """
    Parses command line arguments.

    Returns
    -------
    argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Skip the review stage for a percentage of items"
    )
    parser.add_argument("--api_key", required=True, help="API key")
    return parser.parse_args()


def create_payload(
    dataset_id: str, item_id: str, complete_stage_id: str, workflow_id: str
) -> Dict:
    """
    Creates the payload for the request.

    Parameters
    ----------
    dataset_id (str): Dataset ID
    item_id (str): Item ID
    complete_stage_id (str): Complete stage ID
    workflow_id (str): Workflow ID

    Returns
    -------
    Dict: Payload for the request
    """
    return {
        "filters": {"dataset_ids": [dataset_id], "item_ids": [item_id]},
        "stage_id": complete_stage_id,
        "workflow_id": workflow_id,
    }


def main():
    args = parse_arguments()

    # Can obtain using API requests or finding in the UI
    complete_stage_id = "<complete-stage-id>"
    workflow_id = "<workflow-stage-id>"

    # Can obtain from the webhook payload
    team_slug = "<team-slug>"
    item_id = "<item-id>"
    dataset_id = "<dataset-id>"

    threshold = random.randint(100)

    # Triggered if threshold below 50 (50% of cases)
    if threshold < 50:
        url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/stage"

        payload = create_payload(dataset_id, item_id, complete_stage_id, workflow_id)

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"ApiKey {args.api_key}",
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.text)

    else:
        print("Not skipped. Item goes to review")


if __name__ == "__main__":
    main()
