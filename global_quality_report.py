'''
# Script name: global_quality_report.py
# Author: John Wilkie
# Email: john@v7labs.com
# Last edited: 11.08.23

DESCRIPTION
When executed from the command line, this script:
- 1: Generates a combined quality report for all datasets in a Darwin team using API requests.
     This output is saved as a .csv file 
- 2: If the user specifies an output directory that does not exist,
     the option is given to create the directory and continue

USAGE
python3 global_qualtiy_report.py [-h] [-o OUTPUT_DIR] [-f FILENAME] api_key team_slug

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
team_slug: The slug for your team

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
from time import sleep

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
        'team_slug',
        help='Team slug for your Darwin team'
    )
    parser.add_argument(
        '-o', '--output_dir',
        default=Path.cwd(),
        type=Path,
        help='Output directory for the report (defaults to the current working directory)'
    )
    parser.add_argument(
        '-f', '--filename',
        default='global_quality_report.csv',
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
    filename: str,
    team_slug: str,
    headers: Dict[str, str]
    ) -> None:
    '''
    Validates the given output directory and filename.
    If the output directory does not exist, give the option to create it and continue.

    Parameters
    ----------
        output_dir (Path): The output directory for the generated CSV file
        filename (str): The name of the generated CSV file
        team_slug (str): The Darwin team_slug
        headers (dict): Headers used for the API request

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
    
    url = f'{DARWIN_API_URL}/api/teams/{team_slug}/annotation_classes'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f'Unable to find the team: {team_slug}')

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

def generate_reports(
    team_slug: str,
    datasets: List[Dict[str, str]],
    headers: Dict[str, str]
    ) -> Dict[str, str]:
    '''
    Generates a report for each dataset in a Darwin team

    Parameters
    ----------
        team_slug (str): The Darwin team_slug
        datasets (list[dict]): List of dicts containing information about each dataset in the team
        headers (dict): Headers used for the API request

    Returns
    -------
        report_ids (dict): A dictionary of dataset slugs and report IDs
    
    Raises
    ------
        ValueError: If the report generation fails for any dataset
    '''
    report_ids = {}
    for dataset in datasets:
        url = f'{DARWIN_API_URL}/api/teams/{team_slug}/{dataset["slug"]}/item_reports'
        response = requests.post(url, headers=headers)
        if response.status_code != 201:
            raise ValueError(f'Unable to generate report for dataset: {dataset["slug"]}')
        else:
            print(f'Successfully started report generation for dataset: {dataset["slug"]}')
            # Next, need to pull out the report_id from the response
            report_ids[dataset["slug"]] = response.json()['id']

    return report_ids

def get_report_data(
    team_slug: str,
    report_ids: Dict[str, str],
    headers: Dict[str, str]
    ) -> List[List[str]]:
    '''
    Returns a list of lists containing the report data for each dataset in a Darwin team

    Parameters
    ----------
        team_slug (str): The Darwin team_slug
        report_ids (dict): A dictionary of dataset slugs and report IDs
        headers (dict): Headers used for the API request

    Returns
    -------
        report_data (list[list[str]]): A list of lists containing the report data for each dataset in a Darwin team
    '''

    report_data = []
    first_dataset = True
    while report_ids:
        ready, not_ready = {}, []
        for dataset_slug, report_id in report_ids.items():
            url = f'{DARWIN_API_URL}/api/teams/{team_slug}/{dataset_slug}/item_reports'
            response = requests.get(url, headers=headers)
            for report in response.json():
                if report['id'] == report_id:
                    if report['state'] == 'finished':
                        ready[dataset_slug] = report['url']
                    else:
                        not_ready.append(dataset_slug)

        if ready:
            for dataset in ready:
                url = ready[dataset]
                response = requests.get(url, headers=headers)  
            
                if not response.text:
                    print(f'Dataset {dataset} is empty, skipping...')
                    report_ids.pop(dataset)
                    continue
                else:
                    reader = csv.reader(response.text.splitlines())
                    
                if first_dataset:
                    report_data += list(reader)
                    first_dataset = False
                else:
                    next(reader)
                    report_data += list(reader)

                report_ids.pop(dataset)

        if not_ready:
            print(f'Waiting for reports to be generated for dataset(s): {not_ready}')
            sleep(5)
    
    print('All reports retrieved!')
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

    headers = {
        'accept': 'application/json',
        'Authorization': f'ApiKey {args.api_key}'
    }

    validate_arguments(args.output_dir, args.filename, args.team_slug, headers)

    # Get & save report data
    team_id = get_team_id(headers)
    datasets = get_dataset_ids(headers)
    report_ids = generate_reports(args.team_slug, datasets, headers)
    report_data = get_report_data(args.team_slug, report_ids, headers)
    save_report_to_csv(report_data, args.output_dir, args.filename)

if __name__ == '__main__':
    main()
