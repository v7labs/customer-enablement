'''
# Script name: create-standard-workflow.py
# Last edited: 27.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Creates a standard annotate, review, complete workflow

USAGE
python3 create-standard-workflow.py [-h] api_key team_slug 

REQUIRED ARGUMENTS
api_key: API key for authentication with Darwin
team_slug: slugified version of the team name

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

import requests
import uuid
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
    Top level function to execute.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    dataset_stage_id = str(uuid.uuid4())
    annotator_stage_id = str(uuid.uuid4())
    review_stage_id = str(uuid.uuid4())
    complete_stage_id = str(uuid.uuid4())

    dataset_edge_id = str(uuid.uuid4())
    annotate_edge_id = str(uuid.uuid4())
    review_stage_accept_edge_id = str(uuid.uuid4())
    review_stage_reject_edge_id = str(uuid.uuid4())

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"ApiKey {args.api_key}"
    }

    payload = {
        "name": "ASDJHKAHSDJAHKJDHA1D3",
        "stages": [
            {
                "config": {
                    "initial": True,
                    "dataset_id": None,
                    "x": 2942,
                    "y": 2896
                },
                "edges": [
                    {
                        "id": dataset_edge_id,
                        "source_stage_id": dataset_stage_id,
                        "target_stage_id": annotator_stage_id,
                        "name": "default"
                    }
                ],
                "id": dataset_stage_id,
                "name": "Dataset",
                "type": "dataset"
            },
            {
                "assignable_users": [],
                "config": {
                    "assignable_to": "anyone",
                    "initial": False,
                    "x": 3330,
                    "y": 2896
                },
                "edges": [
                    {
                        "id": annotate_edge_id,
                        "source_stage_id": annotator_stage_id,
                        "target_stage_id": review_stage_id,
                        "name": "default"
                    }
                ],
                "id": annotator_stage_id,
                "name": "Annotate",
                "type": "annotate"
            },
            {
                "assignable_users": [],
                "config": {
                    "assignable_to": "anyone",
                    "initial": False,
                    "readonly": False,
                    "x": 3746,
                    "y": 2896
                },
                "edges": [
                    {
                        "id": review_stage_accept_edge_id,
                        "source_stage_id": review_stage_id,
                        "target_stage_id": complete_stage_id,
                        "name": "approve"
                    },
                    {
                        "id": review_stage_reject_edge_id,
                        "source_stage_id": review_stage_id,
                        "target_stage_id": annotator_stage_id,
                        "name": "reject"
                    }
                ],
                "id": review_stage_id,
                "name": "Review",
                "type": "review"
            },
            {
                "config": {
                    "x": 4061,
                    "y": 2896
                },
                "edges": [],
                "id": complete_stage_id,
                "name": "Complete",
                "type": "complete"
            }
        ]
    }

    response = requests.post(
    f"https://darwin.v7labs.com/api/v2/teams/{args.team_slug}/workflows",
    headers=headers,
    json=payload
    )

    if not response.ok:
        print("request failed", response.status_code, response.text)
    else:
        print("success")

if __name__ == '__main__':
    main()