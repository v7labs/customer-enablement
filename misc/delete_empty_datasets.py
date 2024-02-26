"""
# Script name: delete_empty_datasets.py
# Author: John Wilkie
# Email: john@v7labs.com
# Last edited: 07.01.24

DESCRIPTION
When executed from the command line, this script:
- 1: Gathers all empty datasets in a Darwin team specified by the given API key
- 2: Gives the option to permanently delete these datasets

USAGE
python3 delete_empty_dataset.py [-h] api_key

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

# Import statements
import argparse
import requests
import json
import re
from typing import Dict


def get_args() -> argparse.Namespace:
    """
    Parse and return command line arguments.

    Returns
    -------
        args (argparse.Namespace): API key
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("api_key", help="API key for authentication with Darwin")
    return parser.parse_args()


def validate_api_key(api_key: str) -> None:
    """
    Validates the given API key. Exits if validation fails.

    Parameters
    ----------
        api_key (str): The API key to be validated

    Raises
    ------
        ValueError: If the API key failed validation
    """
    example_key = "DHMhAWr.BHucps-tKMAi6rWF1xieOpUvNe5WzrHP"
    api_key_regex = re.compile(r"^.{7}\..{32}$")
    assert api_key_regex.match(
        api_key
    ), f"Expected API key to match the pattern: {example_key}"


def get_empty_datasets(headers: Dict[str, str]) -> Dict:
    """
    Gets the dataset_id(s) and name(s) of all empty datasets in a Darwin team.

    Parameters
    ----------
        headers (Dict[str, str]): API request headers

    Returns
    -------
        empty_datasets (Dict): Dictionary of empty dataset_id(s) and name(s)
    """
    url = "https://darwin.v7labs.com/api/datasets"
    response = requests.get(url, headers=headers)
    datasets = json.loads(response.text)
    empty_datasets = {}
    for dataset in datasets:
        if dataset["num_items"] == 0:
            empty_datasets[dataset["id"]] = dataset["name"]

    return empty_datasets


def option_to_exit(empty_datasets: Dict) -> bool:
    """
    Gives the option to abort the deletion of empty datasets.

    Parameters
    ----------
        empty_datasets (Dict): Dictionary of empty dataset_id(s) and name(s)
    """
    print(
        "=============================\n\
########## WARNING ##########\n\
=============================\n\nThe following datasets will be permanently deleted should you choose to continue:\n"
    )
    for dataset_id in empty_datasets:
        print(f"Name: {empty_datasets[dataset_id]} with dataset_id: {dataset_id}")
    delete = input("\nContinue? (y/n)\n")
    if delete.lower() != "y":
        print("Exiting...")
        exit()


def disconnect_workflows(empty_datasets: Dict, headers: Dict[str, str]) -> None:
    """
    Disconnects workflows from empty datasets

    Parameters
    ----------
        empty_datasets (Dict): Dictionary of empty dataset_id(s) and name(s)
        headers (Dict[str, str]): API request headers
    """
    url = "https://darwin.v7labs.com/api/datasets"
    response = requests.get(url, headers=headers)
    team_slug = json.loads(response.text)[0]["team_slug"]

    print("Disconnecting workflows...")
    for dataset_id in empty_datasets:
        url = f"https://darwin.v7labs.com/api/datasets/{dataset_id}"
        response = requests.get(url, headers=headers)
        workflow_id = json.loads(response.text)["workflow_ids"]
        if len(workflow_id) != 0:
            print(
                f"Disconnecting workflow_id {workflow_id} from dataset {empty_datasets[dataset_id]}..."
            )
            url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/workflows/{workflow_id[0]}/unlink_dataset"
            response = requests.patch(url, headers=headers)


def delete_empty_datasets(empty_datasets: Dict, headers: Dict[str, str]) -> None:
    """
    Deletes the given empty datasets.

    Parameters
    ----------
        empty_datasets (Dict): Dictionary of empty dataset_id(s) and name(s)
        headers (Dict[str, str]): API request headers
    """
    for dataset_id in empty_datasets:
        print(
            f"Deleting dataset {empty_datasets[dataset_id]} with dataset_id: {dataset_id}..."
        )
        url = f"https://darwin.v7labs.com/api/datasets/{dataset_id}/archive"
        requests.put(url, headers=headers)
    print("Done!")


def main() -> None:
    """
    Top level function to execute sub-functions
    """

    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    # Define API request headers
    headers = {"accept": "application/json", "Authorization": f"ApiKey {args.api_key}"}

    # Get list of empty datasets
    empty_datasets = get_empty_datasets(headers)

    # Give the option to abort deletion
    option_to_exit(empty_datasets)

    # Disconnect workflows & delete datasets
    disconnect_workflows(empty_datasets, headers)
    delete_empty_datasets(empty_datasets, headers)


if __name__ == "__main__":
    main()
