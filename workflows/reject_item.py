"""
# Script name: reject_item.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Checks the status of a given item in V7
- 2: If the item is in the review stage, it sends a command to reject the item

USAGE
python reject_item.py [-h] --item_id ITEM_ID --team_slug TEAM_SLUG --api_key API_KEY --stage_id STAGE_ID

REQUIRED ARGUMENTS
--item_id ITEM_ID   The ID of the item to be rejected
--team_slug TEAM_SLUG   The slug of the team that owns the item
--api_key API_KEY   The API key for authentication
--stage_id STAGE_ID The ID of the stage where the item is located
"""

import argparse
import requests
import json
from typing import Optional


def item_status(item_id: str, team_slug: str, API_KEY: str) -> Optional[str]:
    """
    Returns current status of item_id in V7

    Parameters
    ----------
        item_id (str): The ID of the item
        team_slug (str): The slug of the team that owns the item
        API_KEY (str): The API key for authentication

    Returns
    -------
        status (str): The status of the item
    """
    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/{item_id}?include_thumbnails=false&include_first_sections=false"

    headers = {"accept": "application/json", "Authorization": f"ApiKey {API_KEY}"}

    response = requests.get(url, headers=headers)

    response_json = json.loads(response.text)

    try:
        return response_json["status"]
    except Exception as e:
        print(f"No item status. Check that this item_id is correct. Error: {e}")
        return None


def reject_item(item_id: str, team_slug: str, API_KEY: str, stage_id: str) -> None:
    """
    Rejects a V7 item in the review stage

    Parameters
    ----------
        item_id (str): The ID of the item
        team_slug (str): The slug of the team that owns the item
        API_KEY (str): The API key for authentication
        stage_id (str): The ID of the stage where the item is located

    Raises
    ------
        AssertionError: If the item is not in the review stage
    """
    # Item needs to be in the review stage
    assert (
        item_status(item_id, team_slug, API_KEY) == "review"
    ), "Item needs to be in the review stage to be rejected."

    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/{item_id}/commands"

    payload = {
        "commands": [
            {
                "type": "transition_via_edge",
                "data": {"delay_ms": 6000, "stage_id": stage_id, "edge": "reject"},
            }
        ]
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {API_KEY}",
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)


def main():
    parser = argparse.ArgumentParser(description="Reject an item in V7.")
    parser.add_argument(
        "--item_id", required=True, help="The ID of the item to be rejected"
    )
    parser.add_argument(
        "--team_slug", required=True, help="The slug of the team that owns the item"
    )
    parser.add_argument(
        "--api_key", required=True, help="The API key for authentication"
    )
    parser.add_argument(
        "--stage_id",
        required=True,
        help="The ID of the stage where the item is located",
    )

    args = parser.parse_args()

    reject_item(args.item_id, args.team_slug, args.api_key, args.stage_id)


if __name__ == "__main__":
    main()
