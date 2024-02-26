"""
# Script name: copy_classes.py
# Author: John Wilkie
# Email: john@v7labs.com
# Last edited: 07.01.24

DESCRIPTION
When executed from the command line, this script:
- 1: Gets the annotation classes for the input dataset
- 2: Creates a new dataset with the input name. If it already exists, connect to it instead
- 3: Adds the annotation classes to the new dataset

USAGE
python3 copy_classes.py [-h] api_key existing_dataset_name new_dataset_name

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
existing_dataset: Name of the existing dataset
new_dataset: Name of the new dataset

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
import darwin
import re
from darwin.client import Client
from darwin.datatypes import AnnotationClass


def get_args() -> argparse.Namespace:
    """
    Parse and return command line arguments.

    Returns
    -------
        args (argparse.Namespace): API key, existing dataset name, new dataset name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("api_key", help="API key for authentication with Darwin")
    parser.add_argument("existing_dataset", help="Name of the existing dataset")
    parser.add_argument("new_dataset", help="Name of the new dataset")
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


def copy_classes(api_key: str, existing_dataset: str, new_dataset: str) -> None:
    """
    Copies annotation classes from an existing dataset to a new dataset in Darwin.

    Parameters
    ----------
        api_key (str): The API key for authentication with Darwin
        existing_dataset (str): Name of the existing dataset
        new_dataset (str): Name of the new dataset
    """
    client = Client.from_api_key(api_key)
    existing_dataset = client.get_remote_dataset(
        existing_dataset.lower().strip().replace(" ", "-")
    )

    try:
        new_dataset = client.create_dataset(new_dataset)
        print("New dataset created.")
    except darwin.exceptions.NameTaken:
        new_dataset = client.get_remote_dataset(
            new_dataset.lower().strip().replace(" ", "-")
        )
        print("Dataset name already created, connected to existing.")

    class_list = existing_dataset.fetch_remote_classes()

    for _class in class_list:
        new_dataset.add_annotation_class(
            AnnotationClass(_class["name"], _class["annotation_types"][0])
        )


def main() -> None:
    """
    Top level function to execute sub-functions.
    """
    args = get_args()
    validate_api_key(args.api_key)
    copy_classes(args.api_key, args.existing_dataset, args.new_dataset)


if __name__ == "__main__":
    main()
