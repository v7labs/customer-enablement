"""
# Script name: get_dataset_sizes.py
# Last edited: 07.01.24

DESCRIPTION
When executed from the command line, this script:
- 1: Gets the total size in bytes of all files in each dataset in a Darwin team.
     These values are converted to megabytes and saved as a .json file
- 2: If the user specifies an output directory that does not exist,
     the option is given to create the directory and continue

USAGE
python3 get_dataset_sizes.py [-h] [-o OUTPUT_DIR] [-f FILENAME] api_key

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
-o, --output-dir    Specify the output directory for the .json file. Defaults to the current working directory
-f, --filename      Specify the filename for the .json file. Defaults to "dataset_sizes.json"
"""

import argparse
import requests
import json
import re
from pathlib import Path
from typing import Dict, List


def get_args() -> argparse.Namespace:
    """
    Parse and return command line arguments.

    Returns
    -------
        args (argparse.Namespace): API key, output directory and filename
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("api_key", help="API key for authentication with Darwin")
    parser.add_argument(
        "-o",
        "--output_dir",
        default=Path.cwd(),
        type=Path,
        help="Output directory for the .json file (defaults to the current working directory)",
    )
    parser.add_argument(
        "-f",
        "--filename",
        default="dataset_sizes.json",
        help='Filename for the .json file (defaults to "dataset_sizes.json")',
    )
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


def validate_arguments(output_dir: Path, filename: str) -> None:
    """
    Validates the given output directory and filename.
    If the output directory does not exist, give the option to create it and continue.

    Parameters
    ----------
        output_dir (Path): The output directory for the .json file
        filename (str): The filename for the .json file

    Raises
    ------
        ValueError: If the filename does not end with ".json" or the output directory does not exist and was not created
    """

    if not output_dir.is_dir():
        create_dir = input(
            f"The directory {output_dir} does not exist. Do you want to createit and continue? (y/n)\n"
        )
        if create_dir.lower() == "y":
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"Directory {output_dir} created.")
        else:
            raise ValueError(
                f"Output directory {output_dir} does not exist and was not created."
            )

    if not filename.endswith(".json"):
        raise ValueError(
            "Expected filename to end with .json\n(example: dataset_sizes.json)"
        )


def get_dataset_ids(headers: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Returns a list of dataset_ids in a Darwin team.

    Parameters
    ----------
        headers (dict): Headers used for the API request

    Returns
    -------
        dataset_ids (List[Dict[str, str]]):  a list of dataset_ids in a Darwin team
    """
    url = "https://darwin.v7labs.com/api/datasets"
    response = requests.get(url, headers=headers)
    return response.json()


def get_team_slug(headers: Dict[str, str]) -> str:
    """
    Returns the team slug for a Darwin team.

    Parameters
    ----------
        headers (dict): Headers used for the API request

    Returns
    -------
        team_slug (str): The team slug for a Darwin team
    """
    url = "https://darwin.v7labs.com/api/datasets"
    response = requests.get(url, headers=headers)
    return json.loads(response.text)[0]["team_slug"]


def get_dataset_sizes(
    datasets: List[Dict[str, str]], team_slug: str, headers: Dict[str, str]
) -> Dict[str, float]:
    """
    Returns the total size in megabytes of all files in each dataset in a Darwin team.

    Parameters
    ----------
        datasets (List[Dict[str, str]]): List of dicts containing information about each dataset in the team
        headers (dict): Headers used for the API request

    Returns
    -------
        dataset_sizes (Dict[str, float]): A dict containing the total size in megabytes of all files in each dataset in the team
    """
    dataset_sizes = {}
    for idx, dataset in enumerate(datasets):
        if dataset["name"] == "coco":
            continue
        print(f'Processing dataset: {dataset["name"]} with id: {dataset["id"]}')
        dataset_fully_processed = False
        dataset_size_megabytes = 0
        offset = 0
        while dataset_fully_processed is False:
            url = f'https://darwin.v7labs.com/api/v2/teams/{team_slug}/items?dataset_ids={dataset["id"]}&page[offset]={offset}'
            response = (requests.get(url, headers=headers)).json()
            for item in response["items"]:
                for slot in item["slots"]:
                    try:
                        dataset_size_megabytes += slot["size_bytes"] / 1000000
                    except KeyError:
                        print("Could not get item size")

            if response["page"]["next"] is None:
                dataset_sizes[dataset["name"]] = dataset_size_megabytes
                dataset_fully_processed = True
                print(
                    f'Dataset: {dataset["name"]} fully processed, total size: {dataset_size_megabytes} MB\n'
                )
            else:
                offset += 500
                print(
                    f'Dataset: {dataset["name"]} not yet fully processed. Cumulative size: {dataset_size_megabytes} MB. Continuing with offset: {offset}'
                )

    return dataset_sizes


def save_sizes(
    dataset_sizes: Dict[str, float], output_dir: Path, filename: str
) -> None:
    """
    Saves the dataset sizes to a .json file.

    Parameters
    ----------
        dataset_sizes (Dict[str, float]): A dict containing the total size in megabytes of all files in each dataset in the team
        output_dir (Path): The output directory for the .json file
        filename (str): The filename for the .json file
    """
    output_path = output_dir / filename
    with output_path.open("w") as file:
        json.dump(dataset_sizes, file, indent=4)
    print(f"File saved at {output_path}")


def main() -> None:
    """
    Top level functiion to execute sub-functions.
    """
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)
    validate_arguments(args.output_dir, args.filename)

    # Define API request headers
    headers = {"accept": "application/json", "Authorization": f"ApiKey {args.api_key}"}

    # Get & save progress data
    datasets = get_dataset_ids(headers)
    team_slug = get_team_slug(headers)
    dataset_sizes = get_dataset_sizes(datasets, team_slug, headers)
    save_sizes(dataset_sizes, args.output_dir, args.filename)


if __name__ == "__main__":
    main()
