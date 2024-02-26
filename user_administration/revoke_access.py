"""
# Script name: revoke_access.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Revokes a user's access to a V7 team

USAGE
python revoke_access.py [-h] --user_id USER_ID --api_key API_KEY

REQUIRED ARGUMENTS
--user_id USER_ID   The ID of the user to revoke access from
--api_key API_KEY   The API key to authenticate the request

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
import logging
import requests
from typing import Tuple


def parse_arguments() -> Tuple[str, str]:
    """
    Parses command line arguments.

    Returns
    -------
    user_id (str): The ID of the user to revoke access from
    api_key (str): The API key to authenticate the request
    """
    parser = argparse.ArgumentParser(description="Revoke a user's access to a V7 team")
    parser.add_argument(
        "--user_id", required=True, help="The ID of the user to revoke access from"
    )
    parser.add_argument(
        "--api_key", required=True, help="The API key to authenticate the request"
    )
    args = parser.parse_args()
    return args.user_id, args.api_key


def revoke_access(user_id: str, api_key: str) -> None:
    """
    Revokes a user's access to a V7 team.

    Parameters
    ----------
    user_id (str): The ID of the user to revoke access from
    api_key (str): The API key to authenticate the request

    Raises
    ------
    Exception: If there is an error removing the team member
    """
    url = f"https://darwin.v7labs.com/api/memberships/{user_id}"
    headers = {"accept": "application/json", "Authorization": f"ApiKey {api_key}"}
    response = requests.delete(url, headers=headers)
    if response.ok:
        logging.info(f"User: {user_id} has been removed from your V7 team")
    else:
        logging.error(f"Error removing team member {user_id}")
        raise Exception(f"Error removing team member {user_id}")


def main() -> None:
    user_id, api_key = parse_arguments()
    revoke_access(user_id, api_key)


if __name__ == "__main__":
    main()
