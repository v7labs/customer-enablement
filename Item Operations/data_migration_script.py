'''
# Script name: data_migration_script.py
# Last edited: 15.11.23

DESCRIPTION
When executed from the command line, this script:
- 1: Pulls existing datasets from Darwin with their corresponding annotations
- 2: Filters based on certain classes and moves them to a new dataset locally
- 3: Pushes the new subset of data to a new dataset on Darwin and keeps their original workflow stages

USAGE
python3 data_migration_script.py [-h] api_key team_slug old_datasets_slug old_dataset_ids latest_export new_dataset

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
team_slug: slugified version of the team name
old_datasets_slug: list of the existing datasets to pull data from, seperated by commas
old_dataset_ids: list of the ids of the existing datasets seperated by commas
latest_export: name of the latest export
new_dataset: name of the new dataset to create

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

import json
import os
import shutil
import darwin.importer as importer
from darwin.client import Client
from darwin.importer import get_importer
from darwin.cli_functions import pull_dataset
from pathlib import Path
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
        'team_slug',
        help='slugified version of the team name'
    )
    parser.add_argument(
        'old_datasets_slugs',
        help='list of the existing datasets to pull data from, seperated by commas'
    )
    parser.add_argument(
        'old_dataset_ids',
        help='list of the ids of the current datasets seperated by commas'
    )
    parser.add_argument(
        'latest_export',
        help='name of the latest export'
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


# Step 1: Pull data and annotations using the SDK
def pull_data_and_annotations(api_key, old_datasets_slugs, team_slug, latest_export):
    client = Client.from_api_key(api_key)

    for old_dataset_slug in old_datasets_slugs:
        dataset = client.get_remote_dataset(dataset_identifier=f"{team_slug}/{old_dataset_slug}")
        release = dataset.get_release(f"{latest_export}") # replace this name with the name of the latest release you want to pull
        dataset.pull(release=release)
        #old_dataset_ids.append(dataset.dataset_id)

# Step 2: Specify the class you want to filter for, in str format
def specify_classes_and_filter(latest_export):
    target_classes = []

    # Step 3: Code for looping through images and finding files with specific annotations
    base_dirs = ['', '', '']  # Add paths for each old dataset locally
    # Specify the directory where you want to move images with the specified class
    output_dir = ''
    output_annotations_dir = ''

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create the output directory for annotations if it doesn't exist
    if not os.path.exists(output_annotations_dir):
        os.makedirs(output_annotations_dir)


    for i, base_dir in enumerate(base_dirs):
        annotations_dir = os.path.join(base_dir, f'releases/{latest_export}/annotations')

        for root, _, files in os.walk(annotations_dir):
            for file in files:
                if file.endswith('.json'):
                    annotation_file_path = os.path.join(root, file)

                    with open(annotation_file_path, 'r') as f:
                        annotation_data = json.load(f)

                    image_filename = annotation_data['item']['name']
                    annotations = annotation_data.get('annotations', [])

                    for annotation in annotations:
                        class_name = annotation.get('name', '')

                        if class_name in target_classes:
                            image_src = os.path.join(base_dir, 'images', image_filename)
                            image_dest = os.path.join(output_dir, image_filename)
                            shutil.move(image_src, image_dest)
                            print(f"Moved {image_filename} to {output_dir}")

                            annotation_dest = os.path.join(output_annotations_dir, file)
                            shutil.move(annotation_file_path, annotation_dest)
                            print(f"Moved {file} to {output_annotations_dir}")

                            break

    print("Done!")
    return output_dir, output_annotations_dir


# Step 3: Create new dataset in Darwin to put these in and upload
def upload_to_darwin(output_dir, output_annotations_dir, api_key, new_dataset):
    client = Client.from_api_key(api_key)
    dataset_new = client.create_dataset(new_dataset)

    # Step 5: Upload data from new folder to this dataset and import annotations also, again easier from command line
    dataset_new.push(output_dir)

    # fetch parser objects to import annotations in the correct format and specify the annotations path
    parser = get_importer("darwin")
    annotation_paths = [file for file in Path(output_annotations_dir).rglob("*.json")]
    importer.import_annotations(dataset_new, parser, annotation_paths, append=True)


# Step 4: Filter for the workflow stage which they were in already
# First we need the API call to get workflow stage, we want to do this for all datasets
def get_workflow_stages_and_assign(old_dataset_ids, team_slug, api_key, output_dir):
    # Combine old dataset ids into a comma-separated string
    dataset_ids_str = "%2C".join(map(str, old_dataset_ids))
    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items?dataset_ids={dataset_ids_str}&include_thumbnails=false&include_dicom_json=false&include_first_sections=false&include_workflow_data=false&include_tags=false&include_evaluation_metrics_run_data=false"

    headers = {
        "accept": "application/json",
        "Authorization": f"ApiKey {api_key}"
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)

    ## Get statusus
    # Initialize a dictionary to store filenames and their statuses
    file_statuses = {}

    # Loop through your new dataset files
    for filename in os.listdir(output_dir):
        # Search for the status in the JSON data
        status = None
        for item in data.get("items", []):
            if item.get("name") == filename:
                status = item.get("status")
                break

        # Store the filename and status in the dictionary
        file_statuses[filename] = status

    # Print the filename-status mapping
    for filename, status in file_statuses.items():
        print(f"File: {filename}, Status: {status}")


    # Stage 7: Use get_workflow api to get the id associated with the stage name and add to the file_statuses dict
    new_dataset_workflowid = ""
    import requests

    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/workflows/{new_dataset_workflowid}"

    headers = {
        "accept": "application/json",
        "Authorization": f"ApiKey {api_key}"
    }

    response = requests.get(url, headers=headers)
    data_status_id = json.loads(response.text)

    # Create a new dictionary to store the stage_name and stage_id
    stage_name_id_dict = {}

    # Loop through the stages in the JSON data
    for stage in data_status_id.get("stages", []):
        stage_name = stage.get("name")
        stage_id = stage.get("id")
        stage_name_id_dict[stage_name] = stage_id

    # Print the new dictionary containing stage_name and stage_id
    for stage_name, stage_id in stage_name_id_dict.items():
        print(f"Stage Name: {stage_name}, Stage ID: {stage_id}")


    # Define a mapping from status to stage name
    status_to_stage_mapping = {
        'annotate': 'Annotate',
        'new': 'Dataset',
        'review': 'Review',
        'complete': 'Complete',
    }

    # Create a new dictionary to store the mapping of file names to stage IDs
    file_stage_id_mapping = {}

    # Loop through the file_status_dict
    for filename, status in file_statuses.items():
        # Map the status to the corresponding stage name
        stage_name = status_to_stage_mapping.get(status)
        
        # If a valid stage name is found, get the stage ID from stage_name_id_dict
        if stage_name and stage_name in stage_name_id_dict:
            stage_id = stage_name_id_dict[stage_name]
            file_stage_id_mapping[filename] = stage_id

    # Print the file-stage ID mapping
    for filename, stage_id in file_stage_id_mapping.items():
        print(f"File: {filename}, Stage ID: {stage_id}")


    # Stage 8: Set these stages within the new dataset using the set stage API 
    import requests
    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/stage"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"ApiKey {api_key}"
    }

    dataset_ids = []

    for filename, stage_id in file_stage_id_mapping.items():
        payload = {
            "filters": {
                "item_names": [filename],
                "dataset_ids": dataset_ids
                                },
            "stage_id": stage_id,
            "workflow_id": new_dataset_workflowid
        }

        response = requests.post(url, json=payload, headers=headers)

        print(f"Response for {filename}:")
        print(response.text)
        print()

def main() -> None:
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    # Define API request headers
    headers = {
        'accept': 'application/json',
        'Authorization': f'ApiKey {args.api_key}'
    }

    # Call all functions to do the steps
    pull_data_and_annotations(args.api_key, args.old_datasets_slugs, args.team_slug, args.latest_export)
    specify_classes_and_filter(args.latest_export)
    upload_to_darwin(args.output_dir, args.output_annotations_dir, args.api_key, args.new_dataset)
    get_workflow_stages_and_assign(args.old_dataset_ids, args.team_slug, args.api_key, args.output_dir)


if __name__ == '__main__':
    main()

