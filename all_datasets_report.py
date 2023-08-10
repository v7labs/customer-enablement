'''
# Script name: all_datasets_report.py
# Author: John Wilkie
# Email: john@v7labs.com
=======
# Last edited: 10.08.23

DESCRIPTION
When executed from the command line, this script:
- 1: Generates a combined annotators report for all datasets in a Darwin team using batched (if necessary) API requests.
     This output is saved as a .csv file 
- 2: If the user specifies an output directory that does not exist,
     the option is given to create the directory and continue

USAGE
python3 all_datasets_report.py [-h] [-o OUTPUT_DIR] [-f FILENAME] api_key

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
-o, --output-dir    Specify the output directory for the .csv report. Defaults to the current working directory
-f, --filename      Specify the filename for the .csv report. Defaults to "all_datasets_report.csv" 
'''

import argparse
import requests
import json
import csv
import re
from pathlib import Path
from typing import Tuple, Dict, List

DARWIN_API_URL = 'https://darwin.v7labs.com'

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
        '-o', '--output_dir',
        default=Path.cwd(),
        type=Path,
        help='Output directory for the report (defaults to the current working directory)'
    )
    parser.add_argument(
        '-f', '--filename',
        default='all_datasets_report.csv',
        help='Filename for the generated CSV file (defaults to "all_datasets_report.csv")'
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

def validate_arguments(
    output_dir: Path,
    filename: str
    ) -> None:
    '''
    Validates the given output directory and filename.
    If the output directory does not exist, give the option to create it and continue.

    Parameters
    ----------
        output_dir (Path): The output directory for the generated CSV file
        filename (str): The name of the generated CSV file

    Raises
    ------
        ValueError: If the filename does not end with ".csv" or if the output directory does not exist and was not created
    '''
    if not output_dir.is_dir():
        create_dir = input(f'The directory {output_dir} does not exist. Do you want to create it and continue? (y/n)\n')
        if create_dir.lower() == 'y':
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f'Directory {output_dir} created.')
        else:
            raise ValueError(f'Output directory {output_dir} does not exist and was not created.')

    if not filename.endswith('.csv'):
        raise ValueError(f'Expected filename to end with ".csv"\n(example: annotator_report.csv)')

def get_team_id(
    headers: Dict[str, str]
    ) -> str:
    '''
    Returns the Darwin team_id

    Parameters
    ----------
        headers (dict): Headers used for the API request

    Returns
    -------
         team_id (str): The Darwin team_id
    '''
    url = f'{DARWIN_API_URL}/api/memberships'
    response = requests.get(url, headers=headers)
    return json.loads(response.text)[0]['team_id']

def get_dataset_ids(
    headers: Dict[str, str]
    ) -> List[Dict[str, str]]:
    '''
    Returns a list of dataset_ids in a Darwin team

    Parameters
    ----------
        headers (dict): Headers used for the API request

    Returns
    -------
        dataset_ids (List[Dict[str, str]]):  a list of dataset_ids in a Darwin team
    '''
    url = f'{DARWIN_API_URL}/api/datasets'
    response = requests.get(url, headers=headers)
    return response.json()

def get_report_data(
    headers: Dict[str, str], 
    team_id: str,
    datasets: List[Dict[str, str]],
    batch_size: int=500
    ) -> List[List[str]]:
    '''
    Returns the data needed for a combined annotators report of all datasets.

    Parameters
    ----------
        headers (dict): Headers used for the API request
        team_id (str): The Darwin team ID
        datasets (list[dict]): List of dicts containing information about each dataset in the team
        batch_size (int, optional), The size of the batched API requests. Defaults to 500

    Returns
    -------
        report_data (List[List[str]]): An object containing annotator statistics for all datasets in a Darwin team
    '''
    dataset_count = len(datasets)
    dataset_ids, report_data = [], []
    first_batch = True
    print(f'Generating report for {dataset_count} datasets...')

    for index, dataset in enumerate(datasets, 1):
        dataset_ids.append(dataset['id'])
        is_last_dataset = (index) == dataset_count
        is_batch_full = (index) % batch_size == 0

        if is_batch_full or is_last_dataset:
            print(f'Getting data for datasets {index + 1 - len(dataset_ids)} to {index}...')
            ids_str = ','.join(str(dataset_id) for dataset_id in dataset_ids)
            report_url = f'{DARWIN_API_URL}/api/reports/{team_id}/annotation?group_by=dataset%2Cuser&dataset_ids={ids_str}&granularity=day&format=csv&include=user.email%2Cdataset.name'
            response = requests.get(report_url, headers=headers)
            reader = csv.reader(response.text.splitlines())
            if first_batch:
                first_batch = False
                report_data += list(reader)
            else:
                next(reader)
                report_data += list(reader)
            dataset_ids = []

    print('Done!')
    return report_data

def save_report_to_csv(
    report_data: List[List[str]],
    output_dir: Path,
    filename: str
    ) -> None:
    '''
    Save the report data to a CSV file.

    Parameters
    ----------
        report_data (list[list[str]]): Report data from API requests
        output_dir (str): The output directory for the generated CSV file
        filename (str): The filename of the generated CSV file
    '''
    output_path = output_dir / filename
    with output_path.open('w') as file:
        writer = csv.writer(file)
        writer.writerows(report_data)
    print(f'File saved at {output_path}')

def main() -> None:
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)
    validate_arguments(args.output_dir, args.filename)

    # Define API request headers
    headers = {
        'accept': 'application/json',
        'Authorization': f'ApiKey {args.api_key}'
    }

    # Get & save report data
    team_id = get_team_id(headers)
    datasets = get_dataset_ids(headers)
    report_data = get_report_data(headers, team_id, datasets)
    save_report_to_csv(report_data, args.output_dir, args.filename)

if __name__ == '__main__':
    main()