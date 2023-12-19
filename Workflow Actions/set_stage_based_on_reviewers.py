'''
# Script name: set_stage_based_on_reviewers.py
# Last edited: 28.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Reads in a CSV report and obtains the comment thread of each item_id
- 2: Adds a new column called 'comment_count' based on number of comments
- 3: Sets filters on the report based on comments and the number of reviewers 
- 4: Sends item to specific stage ID's

USAGE
python3 set_stage_based_on_reviewers.py [-h] api_key csv_path dataset_id complete_stage_id review_stage_id new_stage_id

REQUIRED ARGUMENTS
api_key: API key for authentication with Darwin
csv_path: Path of the csv report
dataset_id: ID of the dataset to add instructions to
complete_stage_id: ID of the complete stage within the workflow
review_stage_id: ID of the review stage within the workflow
new_stage_id: ID of the new stage within the workflow

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''


# load csv report
import pandas as pd
from numpy import nan
import json
import requests
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
        'csv_path',
        help='Path of the csv report'
    )
    parser.add_argument(
        'dataset_id',
        help='ID of the dataset to add instructions to'
    )
    parser.add_argument(
        'complete_stage_id',
        help='ID of the complete stage within the workflow'
    )
    parser.add_argument(
        'review_stage_id',
        help='ID of the review stage within the workflow'
    )
    parser.add_argument(
        'new_stage_id',
        help='ID of the new stage within the workflow'
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


def filter_report_and_set_stage(report,dataset_id,complete_stage_id,review_stage_id,new_stage_id,api_key):
    '''
    Modifies the csv report based on the comments and number of reviwers, and sets items to specific stafe accordingly

    Parameters
    ----------
        report (dataframe): CSV report
        dataset_id (str): ID of specific dataset
        complete_stage_id (str): ID of the complete stage within the workflow
        review_stage_id (str): ID of the review stage within the workflow
        new_stage_id (str): ID of the new stage within the workflow
        api_key (str): The API key to use for authentication

    '''

    for row in range(len(report)):
        url = f"https://darwin.v7labs.com/api/v2/teams/nooshin-v7-workspace/items?item_names={report.filename[row]}&dataset_ids=649498&include_thumbnails=false&include_first_sections=false&include_workflow_data=false&include_tags=false&include_evaluation_metrics_run_data=false"

        headers = {
            "accept": "application/json",
            "Authorization": f"ApiKey {api_key}"
        }

        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        id_value = data["items"][0]["id"]
        #print(id_value)
        report.at[row, 'item_id'] = id_value  # Assign the 'id_value' to the 'item_id' column for the current row


        # get comment thread of each item id
        url_comment = f"https://darwin.v7labs.com/api/v2/teams/nooshin-v7-workspace/items/{id_value}/comment_threads"

        headers = {
            "accept": "application/json",
            "Authorization": f"ApiKey {api_key}"
        }

        response = requests.get(url_comment, headers=headers)
        data = json.loads(response.text)

        if len(data)== 0: # means there's no comments 
            #report.at[row, 'comment_count'] = 0
            continue
        elif len(data)>0:
            if data[0]["comment_count"] == 1:
                #report.at[row, 'comment_count'] = 1
                continue
            elif data[0]["comment_count"] > 1:
                report.at[row, 'comment_count'] = 2

    #print(report)

    # set the filters on the report
    report.loc[~report['reviewers'].isnull(), 'stage'] = complete_stage_id # if it has reviewers set to complete
    report.loc[report['reviewers'].isnull() & ~report['annotators'].isnull(), 'stage'] = review_stage_id # if only annotators set to review
    report.loc[report['reviewers'].isnull() & report['annotators'].isnull(), 'stage'] = new_stage_id # if none set to new/dataset
    report.loc[~report['reviewers'].isnull() & ~report['comment_count'].isnull(), 'stage'] = review_stage_id # if it has reviewers but count more than one set to review


    url = "https://darwin.v7labs.com/api/v2/teams/nooshin-v7-workspace/items/stage"
    for row in range(len(report)):
        payload = {
            "filters": {
                "dataset_ids": [dataset_id],
                "item_names": [report.filename[row]]
            },
            "workflow_id": "0e89fb3e-0d75-4d48-a385-780ae3a9cd19",
            "stage_id": report.stage[row]
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"ApiKey {api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.text)

def main() -> None:
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    report = pd.read_csv(args.csv_path)
    report.item_id = nan
    report.comment_number = ""

    filter_report_and_set_stage(report,args.dataset_id,args.complete_stage_id,args.review_stage_id,args.new_stage_id,args.api_key)

if __name__ == '__main__':
    main()
