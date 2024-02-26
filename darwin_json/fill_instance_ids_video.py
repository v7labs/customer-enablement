"""
# Script name: fill_instance_ids_video.py
# Last edited: 26.07.23

DESCRIPTION
Before running this script:
- 1: A new review stage called "InstanceIDCheck" must be created in the dataset's workflow
- 2: The variables on lines 40-45 must be populated with the correct values for your team and dataset
- 3: All classes present in the dataset must have the instance ID sub-annotation type enabled

When executed from the command line, this script:
- 1: Moves all items in any review stage or the complete stage to the new review stage
- 2: Creates and pulls an export of all items in review
- 3: Extends the instance ID present in each annotation to all frames in the annotion.
     If no instance ID is present, then one is generated using the API and applied to all frames in the annotation
- 4: Uploads the new annotation file for each item

After running, should anything have gone wrong with the annotation adjustment,
a local copy of the original annotations will have been saved in the current working directory.

USAGE
python3 fill_instance_ids_video.py
"""

from darwin.client import Client
from darwin.dataset import RemoteDataset
from darwin.dataset.release import Release
from darwin.exceptions import NotFound
from darwin.importer import get_importer
import darwin.importer as importer
from pathlib import Path
from time import sleep
import requests
import zipfile
import json

# GLOBALS - To be popoulated per dataset before running
api_key = "api_key"
team_slug = "team_slug"
dataset_slug = "dataset_slug"
dataset_id = (
    000000  # Dataset ID can be found in the URL when viewing the dataset in Darwin
)
workflow_id = "workflow_id"  # Workflow ID can be found in the URL when viewing the workflow in Darwin
target_stage_id = "target_stage_id"  # Stage ID can be found in the URL when viewing the stage in Darwin

# Define a global API client & headers
client = Client.local(team_slug=team_slug)
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"ApiKey {api_key}",
}


def assign_to_instance_id_check_stage():
    payload = {
        "filters": {"statuses": ["review", "complete"], "dataset_ids": [dataset_id]},
        "stage_id": target_stage_id,
        "workflow_id": workflow_id,
    }
    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/stage"
    requests.post(url, json=payload, headers=headers)


def create_and_pull_release():
    payload = {
        "filters": {"statuses": ["review"]},
        "format": "darwin_json_2",
        "name": f"original_annotations_{dataset_slug}",
    }
    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/datasets/{dataset_slug}/exports"
    requests.post(url, json=payload, headers=headers)

    dataset: RemoteDataset = client.get_remote_dataset(dataset_slug)
    while True:
        print("Waiting for Release to be created...")
        sleep(5)
        try:
            print("Trying to get release")
            release: Release = dataset.get_release(
                f"original_annotations_{dataset_slug}"
            )

            print("Got Release, downloading it!")
            release.download_zip(Path(f"./original_annotations_{dataset_slug}.zip"))
            with zipfile.ZipFile(
                f"./original_annotations_{dataset_slug}.zip", "r"
            ) as zip_ref:
                zip_ref.extractall(f"./original_annotations_{dataset_slug}/")
            Path(f"./original_annotations_{dataset_slug}.zip").unlink()
            break

        except NotFound:
            print("Release not ready yet!")
            continue


def fill_instance_ids():
    annotation_files = [
        file
        for file in Path(f"./original_annotations_{dataset_slug}/").iterdir()
        if file.is_file() and file.suffix == ".json"
    ]
    Path(f"./adjusted_annotations_{dataset_slug}/").mkdir(parents=True, exist_ok=True)

    for file in annotation_files:
        missing_id_count = 0
        with open(file, "r+") as f:
            data = json.load(f)
            item_id = data["item"]["source_info"]["item_id"]
            for annotation in data["annotations"]:
                instance_id = ""
                frames_missing_instance_id = []
                for frame_idx, frame in annotation["frames"].items():
                    try:
                        instance_id = frame["instance_id"]
                        break
                    except KeyError:
                        frames_missing_instance_id.append(frame_idx)
                        continue

                if not instance_id:
                    print(
                        "No instance ID found for annotation, getting next unique ID from API"
                    )
                    url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/{item_id}/annotations/instance_id"
                    response = requests.post(url, headers=headers)
                    instance_id = response.json()["instance_id"]
                    for frame_idx in frames_missing_instance_id:
                        annotation["frames"][str(frame_idx)]["instance_id"] = {
                            "value": instance_id
                        }
                        missing_id_count += 1
                else:
                    for frame_idx in frames_missing_instance_id:
                        annotation["frames"][str(frame_idx)][
                            "instance_id"
                        ] = instance_id
                        missing_id_count += 1

        print(f"Added instance IDs to {missing_id_count} frames in {file.name}")

        with open(f"./adjusted_annotations_{dataset_slug}/{file.name}", "w") as f:
            json.dump(data, f, indent=4)


def upload_adjusted_annotations():
    files_to_upload = [
        file
        for file in Path(f"./adjusted_annotations_{dataset_slug}/").iterdir()
        if file.is_file() and file.suffix == ".json"
    ]
    dataset: RemoteDataset = client.get_remote_dataset(dataset_slug)
    parser = get_importer("darwin")
    importer.import_annotations(dataset, parser, files_to_upload, append=False)


def main():
    # 1: Move all items in any review stage or the complete stage to the new review stage
    assign_to_instance_id_check_stage()

    # 2: Create and pull an export of all items in review
    create_and_pull_release()

    # 3: Check instance IDs for each item, adjusting the annotation file each time
    fill_instance_ids()

    # 4: Upload the new annotation file for each item
    upload_adjusted_annotations()


if __name__ == "__main__":
    main()
