"""
# Script name: get_dataset_progress.py
# Last edited: 07.01.24

DESCRIPTION
When executed from the command line, this script:
- 1: Gets the progress percentage for each dataset in a Darwin team.
     These values are rounded to 2 decimal places, printed to the console, and saved as a .json file
- 2: If the user specifies an output directory that does not exist,
     the option is given to create the directory and continue

USAGE
python3 get_dataset_progress.py [-h] [-o OUTPUT_DIR] [-f FILENAME] api_key

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
-o, --output-dir    Specify the output directory for the .json report. Defaults to the current working directory
-f, --filename      Specify the filename for the .json report. Defaults to "dataset_progress.json"
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
        help="Output directory for the report (defaults to the current working directory)",
    )
    parser.add_argument(
        "-f",
        "--filename",
        default="dataset_progress.json",
        help='Filename for the generated CSV file (defaults to "dataset_progress.json")',
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
        output_dir (Path): The output directory for the .json report
        filename (str): The filename for the .json report

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
            "Expected filename to end with .json\n(example: dataset_progress.json)"
        )


def get_dataset_ids(headers: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Returns a list of dataset_ids in a Darwin team

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


def get_progress(
    datasets: List[Dict[str, str]], headers: Dict[str, str]
) -> Dict[str, float]:
    """
    Returns the progress percentage for each dataset in a Darwin team.

    Parameters
    ----------
        datasets (List[Dict[str, str]]): List of dicts containing information about each dataset in the team
        headers (dict): Headers used for the API request

    Returns
    -------
        progress_data (Dict[str, float]): A dict containing the progress percentage for each dataset in the team
    """
    progress_data = {}
    for idx, dataset in enumerate(datasets):
        url = f"https://darwin.v7labs.com/api/datasets/{dataset['id']}/report"
        print(
            f"Getting progress of dataset: {dataset['name']} with id: {dataset['id']}..."
        )
        response = requests.get(url, headers=headers)
        progress_percentage = round(response.json().get("progress") * 100, 2)
        progress_data[dataset["name"]] = progress_percentage

    return progress_data


def save_progress(
    progress_data: Dict[str, float], output_dir: Path, filename: str
) -> None:
    """
    Saves the progerssa data to a .json file.

    Parameters
    ----------
        progress_data (Dict[str, float]): A dict containing the progress percentage for each dataset in the team
        output_dir (Path): The output directory for the .json report
        filename (str): The filename for the .json report
    """
    output_path = output_dir / filename
    with output_path.open("w") as file:
        json.dump(progress_data, file, indent=4)
        print(f"Progress data saved to {output_path}.")


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
    progress_data = get_progress(datasets, headers)
    save_progress(progress_data, args.output_dir, args.filename)


if __name__ == "__main__":
    main()
