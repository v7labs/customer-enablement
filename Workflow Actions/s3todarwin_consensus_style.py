'''
# Email: nooshin@v7labs.com
# Last edited: 07.07.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Pulls data from a specific subfolder in S3 where annotation json files are stored
- 2: Compares class name and attribute name between these files
- 3: If class names and attributes are consistent, then no tag is applied, otherwise a diagreement tag is added
- 4: Item is moved to a logic stage where it will move on a different path depending on tag


USAGE
python3 s3todarwin_consensus_style.py [-h] api_key dataset_id team_slug tag_id bucket_name folder_name stage_id workflow_id

REQUIRED ARGUMENTS
api_key: API key for authentication with Darwin
dataset_id: ID of the dataset to add instructions to
team_slug: Slugified version of the team in Darwin
tag_id: ID of the tag annotation class
bucket_name: Name of bucket in S3
folder_name: Name of the folder within S3 bucket
stage_id: ID of the logic stage to move files to
workflow_id: ID of the workflow attched to specific dataset
'''

import json
import boto3
import os
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
        'dataset_id',
        help='ID of the dataset to add instructions to'
    )
    parser.add_argument(
        'team_slug',
        help='Slugified version of the team in Darwin'
    )
    parser.add_argument(
        'tag_id',
        help='ID of the tag annotation class'
    )
    parser.add_argument(
        'bucket_name',
        help='Name of bucket in S3'
    )
    parser.add_argument(
        'folder_name',
        help='Name of the folder within S3 bucket'
    )
    parser.add_argument(
        'stage_id',
        help='ID of the logic stage to move files to'
    )
    parser.add_argument(
        'workflow_id',
        help='ID of the workflow attched to specific dataset'
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


def main() -> None:
    '''
    Top level function to execute main function of script.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    ## These are the varibles which need to be filled out accordingly
    # First two are AWS variables
    os.environ['AWS_ACCESS_KEY_ID'] = ''
    os.environ['AWS_SECRET_ACCESS_KEY'] = ''

    s3_client = boto3.client('s3')

    try:
        response = s3_client.list_objects_v2(Bucket=args.bucket_name, Prefix=args.folder_name)
        json_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.json')]
        
        field_values_class = {}
        field_values_attribute = {}
    
        for file_name in json_files:
            print(file_name)
            response = s3_client.get_object(Bucket=args.bucket_name, Key=file_name)
            content = response['Body'].read().decode('utf-8')
            json_data = json.loads(content)
            data = json.loads(json_data)
            
            class_name = data['annotations'][0]['name']
            class_attribute = data['annotations'][0]['attributes']
            
            field_values_class[file_name] = class_name
            field_values_attribute[file_name] = class_attribute[0]
            item_id = data['item']['source_info']['item_id']
        
        if (len(set(field_values_class.values())) == 1) and (len(set(field_values_attribute.values())) == 1):
            print("All field values are the same")
        else:
            url = f"https://darwin.v7labs.com/api/v2/teams/{args.team_slug}/items/slots/tags"
        
            payload = {
                "filters": {
                    "item_ids": [item_id],
                    "dataset_ids": [args.dataset_id],
                    "select_all": True
                },
                "annotation_class_id": args.tag_id
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": f"ApiKey {args.api_key}"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            print(response.text)
        
    except Exception as e:
        print(f"Error processing JSON files: {e}")

    # also use the set stage API to move straight from holding review stage to logic stage
    import requests
    url = f"https://darwin.v7labs.com/api/v2/teams/{args.team_slug}/items/stage"

    payload = {
        "filters": {
            "item_ids": [item_id],
            "dataset_ids": [args.dataset_id]
        },
        "stage_id": "",
        "workflow_id": ""
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {args.api_key}"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

if __name__ == '__main__':
    main()

        

