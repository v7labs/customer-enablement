"""
This script is designed to be run as an AWS Lambda function. It validates annotations in a given JSON data, checks if all annotations have exactly one attribute, and returns a list of names of all annotations that do not have exactly one attribute. If there are invalid annotations, it changes the stage of an item in a workflow and sends it back to the annotate stage. The script uses the V7 Darwin API for setting the stage of an item.

The main entry point of this script is the `lambda_handler` function, which AWS Lambda invokes to start execution of the Lambda function. This function takes in an `event` object, which contains input data, and a `context` object, which contains information about the runtime the Lambda function is executing in.

The `event` object is expected to have a `body` field containing the JSON data to be processed. The JSON data should include information about the item, source info, dataset, and team.

The script uses the following environment variables:
- `API_KEY`: The API key for the V7 Darwin API.
- `stage_id`: The ID of the annotate stage.
- `workflow_id`: The ID of the workflow.
"""

import json
import requests
import logging
import re

API_KEY = "<API KEY>"
stage_id = "<annotate stage id>"
workflow_id = "<workflow id>"


def valid_annotations(json_data):
    """
    Checks if all annotations have exactly one attribute. Else returns False
    """
    if json_data is None:
        return False

    annotations = json_data.get("annotations", [])

    for annotation in annotations:
        attributes = annotation.get("attributes", [])

        if len(attributes) != 1:
            return False

    return True


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


def find_annotations_with_multiple_attributes(json_data):
    """
    Returns list of names of all anotations that do not have exactly what attribute
    """
    # json_data = json.loads(json_data)
    annotations = json_data.get("annotations", [])
    invalid_annotations = []

    for annotation in annotations:
        attributes = annotation.get("attributes", [])

        if len(attributes) != 1:
            invalid_annotations.append(annotation["name"])

    return invalid_annotations


def set_stage(team_slug, stage_id, workflow_id, item_id, dataset_id):
    """
    Changes the stage of an item in a workflow
    """
    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/stage"

    payload = {
        "filters": {"item_ids": [item_id], "dataset_ids": [dataset_id]},
        "workflow_id": workflow_id,
        "stage_id": stage_id,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {API_KEY}",
    }

    response = requests.post(url, json=payload, headers=headers)
    logging.info("Set stage API response status", response.status_code)


def lambda_handler(event, context):
    body = event["body"]
    body = json.loads(body)
    dataset_url = body["item"]["source_info"]["dataset"]["dataset_management_url"]
    dataset_id = extract_integer_id(dataset_url)
    item_id = body["item"]["source_info"]["item_id"]
    team_slug = body["item"]["source_info"]["team"]["slug"]

    invalid = find_annotations_with_multiple_attributes(body)

    if invalid:
        set_stage(team_slug, stage_id, workflow_id, item_id, dataset_id)
        logging.info("Incorrect number of attributes. Sending back to annotate stage")

    return {"statusCode": 200, "body": json.dumps("Success")}
