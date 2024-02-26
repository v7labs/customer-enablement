"""
# Script name: add_receipt_classes.py
# Last edited: 

DESCRIPTION
When executed from the command line, this script:
- 1: Adds bounding box classes and tag classes to a specified dataset on Darwin.

USAGE
python add_receipt_classes.py [-h] --api_key API_KEY --team_slug TEAM_SLUG --dataset_id DATASET_ID

REQUIRED ARGUMENTS
--api_key API_KEY   Your Darwin API key
--team_slug TEAM_SLUG   Your Darwin team slug
--dataset_id DATASET_ID   The ID of the dataset to which classes should be added

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
import requests


def add_classes(api_key: str, team_slug: str, dataset_id: str) -> None:
    """
    Adds bounding box classes and tag classes to a specified dataset on Darwin.

    Parameters
    ----------
        api_key (str): Your Darwin API key
        team_slug (str): Your Darwin team slug
        dataset_id (str): The ID of the dataset to which classes should be added

    Raises
    ------
        Exception: If the request to add a class fails

    Returns
    -------
        None
    """
    Class_list = [
        "Description",
        "MerchantAddress City",
        "MerchantAddress CountryRegion",
        "MerchantAddress CountryRegion",
        "MerchantAddress PoBox",
        "MerchantAddress PostalCode",
        "MerchantAddress Road",
        "MerchantAddress Road",
        "MerchantAddress State",
        "MerchantAddress StreetAddress",
        "MerchantName",
        "MerchantPhoneNumber",
        "Price",
        "Quantity",
        "ReceiptType",
        "Subtotal",
        "Tip",
        "Total",
        "TotalPrice",
        "TotalTax",
        "TransactionDate",
        "TransactionTime",
    ]
    Tag_list = ["Receipt Layout"]

    url = f"https://darwin.v7labs.com/api/teams/{team_slug}/annotation_classes"

    headers = {"accept": "application/json", "Authorization": f"ApiKey {api_key}"}

    dataset_ids = [{"id": dataset_id}]

    # Adds bounding box classes
    for name in Class_list:
        payload = {
            "annotation_type_ids": [2, 6],
            "datasets": dataset_ids,
            "description": None,
            "images": [],
            "metadata": {"_color": "rgba(97,0,255,1.0)"},
            "name": name,
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.ok:
            print(f"{name} has been added as a class successfully")
        else:
            raise Exception(f"Failed to add class {name}. Response: {response.text}")

    # Adds tag classes
    for tag in Tag_list:
        payload = {
            "annotation_type_ids": [6, 1],
            "datasets": dataset_ids,
            "description": None,
            "images": [],
            "metadata": {"_color": "rgba(0,239,196,1.0)"},
            "name": tag,
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.ok:
            print(f"{tag} has been added as a class successfully")
        else:
            raise Exception(f"Failed to add class {tag}. Response: {response.text}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add bounding box classes and tag classes to a specified dataset on Darwin."
    )
    parser.add_argument("--api_key", required=True, help="Your Darwin API key")
    parser.add_argument("--team_slug", required=True, help="Your Darwin team slug")
    parser.add_argument(
        "--dataset_id",
        required=True,
        help="The ID of the dataset to which classes should be added",
    )
    args = parser.parse_args()

    add_classes(args.api_key, args.team_slug, args.dataset_id)


if __name__ == "__main__":
    main()
