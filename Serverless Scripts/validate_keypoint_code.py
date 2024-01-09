'''
# Script name: validate_keypoint_code.py
# Last edited: 28.11.2023

DESCRIPTION
When executed as a Lambda function, this script:
- 1: Checks if keypoints are in the correct order
- 2: If not, changes their stage in the workflow with a comment attached

USAGE
This script needs to be run as a lambda function on AWS

REQUIRED PARAMETERS
api_key: API key for authentication with Darwin
stage_id: ID of the stage to set the items to
workflow_id: ID of the workflow attched to the dataset

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

import json
import requests
import logging
import re
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

API_KEY = os.environ.get('API_Key')
stage_id = ""
workflow_id = ""


def extract_integer_id(url):
    """
    Extracts the datasetid from a dataset url
    """
    pattern = r"/datasets/(\d+)/"
    match = re.search(pattern, url)
    if match:
        return int(match.group(1))
    else:
        return None



def find_wrong_keypoint_order(json_data):
    """
    Returns a list of names of all annotations that have missing 'instance_id' in any frame
    """
    annotations = json_data.get("annotations", [])
    invalid_annotations = []


    for annotation in annotations:
        frames = annotation.get("frames", {})
        skeleton_nodes = annotations[0].get('skeleton', {}).get('nodes', [])
        
        if len(skeleton_nodes) >= 2:
            first_node = skeleton_nodes[0]
            second_node = skeleton_nodes[1]
            print(second_node['x'])
            print(first_node['x'])
            
            if second_node['x'] < first_node['x']:
                invalid_annotations.append(annotation["name"])
                break  # Break out of the inner loop, as we found a missing 'instance_id' in this annotation

    return invalid_annotations



def set_stage(team_slug,stage_id,workflow_id,item_id,dataset_id):
    """
    Changes the stage of an item in a workflow
    """
    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/stage"

    payload = {
        "filters": {
            "item_ids": [item_id],
            "dataset_ids": [dataset_id]
        },
        "workflow_id": workflow_id,
        "stage_id": stage_id
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {API_KEY}"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    
def add_comment(team_slug,item_id):

    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/{item_id}/comment_threads"

    payload = {
        "bounding_box": {
            "h": 5,
            "w": 5,
            "x": 5,
            "y": 5
        },
        "comments": [{ "body": "The keypoint has been drawn the wrong way. Please correct" }],
        "slot_name": "0"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {API_KEY}"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def lambda_handler(event, context):
    body = event["body"]
    body = json.loads(body)
    dataset_url = body["item"]["source_info"]["dataset"]["dataset_management_url"]
    dataset_id = extract_integer_id(dataset_url)
    item_id = body["item"]["source_info"]["item_id"]
    team_slug = body["item"]["source_info"]["team"]["slug"]
    
    invalid = find_wrong_keypoint_order(body)
    
    if invalid:
        add_comment(team_slug,item_id)
        set_stage(team_slug,stage_id,workflow_id,item_id,dataset_id)
        print("Instance ID missing. Sending back to annotate")
    
    #print("This is the body: ",body)
    #print("These are the invalid annotations: ",invalid)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }

