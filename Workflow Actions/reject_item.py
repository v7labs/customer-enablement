'''
# Script name: reject_item.py
# Last edited: 27.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Rejects an item which is in a particular stage

USAGE
python3 create-standard-workflow.py [-h] api_key team_slug item_id stage_id

REQUIRED ARGUMENTS
api_key: API key for authentication with Darwin
team_slug: slugified version of the team name
item_id: ID of the item to reject
stage_id: ID of the stage which the item is in

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''
import requests
import json
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
        'item_id',
        help='ID of the item to reject'
    )
    parser.add_argument(
        'stage_id',
        help='ID of the stage which the item is in'
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


def item_status(item_id,team_slug, api_key):
    """
    Returns current status of item_id in V7

    Args: item_id, team_slug str

    Returns: status str
    """
    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/{item_id}?include_thumbnails=false&include_first_sections=false"

    headers = {
        "accept": "application/json",
        "Authorization": f"ApiKey {api_key}"
    }

    response = requests.get(url, headers=headers)

    response_json = json.loads(response.text)

    try:
        return response_json["status"]
    except:
        print("No item status. Check that this item_id is correct")



def reject_item(item_id, team_slug, stage_id, api_key):
    """
    Rejects a V7 item in the review stage

    Args: item_id, team_slug str

    Returns: None  
    """
    #Item needs to be in the review stage
    assert item_status(item_id, team_slug) == "review", "Item needs to be in the review stage to be rejected."

    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/{item_id}/commands"

    payload = {"commands":[{"type":"transition_via_edge","data":{"delay_ms":6000,"stage_id":stage_id,"edge":"reject"}}]}

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {api_key}"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)


def main() -> None:
    '''
    Top level function to execute.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    # run the reject_item subfunction
    reject_item(args.item_id, args.team_slug, args.stage_id, args.api_key)


if __name__ == '__main__':
    main()