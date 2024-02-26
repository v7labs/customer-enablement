"""
# Script name: auto-metadata-deletion.py
# Last edited: 19.05.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Deletes a given item in V7
- 2: Deletes all associated metadata in S3

USAGE
python3 auto_metadata_deletion.py [-h] team_slug dataset_id item_name [-s3_path]

REQUIRED ARGUMENTS
team_slug: V7 Team slug
dataset_id: V7 Dataset Id containing item
item_name: Name of Item to be deleted

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
s3_path: Path to item in S3
"""

import boto3
import requests
import os
import argparse
import logging

# Loading environment variables
access_key = os.environ.get("S3_ACCESS_KEY")
secret_key = os.environ.get("S3_SECRET_KEY")
v7_prefix = os.environ.get("V7_STORAGE_PREFIX")
bucket_name = os.environ.get("S3_BUCKET_NAME")
V7_API_KEY = os.environ.get("V7_API_KEY")


def delete_s3_file(bucket_name, file_key, s3_client) -> None:
    """
        Deletes a single item from an S3 bucket.

    Parameters
    ----------
        bucket_name (str): The S3 bucket name where the item is stored
        file_key (str): The path to the item to be deleted

    Returns
    -------
        None
    """
    try:
        # Delete the file from the S3 bucket
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        logging.info(
            f"File '{file_key}' deleted successfully from bucket '{bucket_name}'."
        )
    except Exception as e:
        logging.warning(
            f"Error deleting file '{file_key}' from bucket '{bucket_name}': {str(e)}"
        )


def delete_s3_files_in_path(bucket_name, path, s3_client) -> None:
    """
    Gets the dataset_id(s) and name(s) of all empty datasets in a Darwin team.

    Parameters
    ----------
        bucket_name (str): The S3 bucket name where the item is stored
        file_key (str): The path to the item to be deleted

    Returns
    -------
        None
    """
    try:
        # List all objects in the specified path
        objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path)["Contents"]

        # Delete each object in the path
        for obj in objects:
            s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
            logging.info(
                f"File '{obj['Key']}' deleted successfully from bucket '{bucket_name}'."
            )

        logging.info(
            f"All files in path '{path}' deleted successfully from bucket '{bucket_name}'."
        )
    except Exception as e:
        logging.warning(
            f"Error deleting files in path '{path}' from bucket '{bucket_name}': {str(e)}"
        )


def delete_v7_file(item_name, team_slug, dataset_id) -> None:
    """
    Deletes a V7 file with a given name in the designated dataset

    Parameters
    ----------
        bucket_name (str): The S3 bucket name where the item is stored
        file_key (str): The path to the item to be deleted

    Returns
    -------
        None
    """
    try:
        # Specify header and payload information for V7 item deletion
        url = f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items"

        payload = {"filters": {"item_names": [item_name], "dataset_ids": [dataset_id]}}

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"ApiKey {V7_API_KEY}",
        }

        requests.delete(url, json=payload, headers=headers)
        logging.info(
            f"File '{item_name}' deleted successfully from V7 Dataset: '{dataset_id}'."
        )

    except Exception as e:
        logging.warning(
            f"Error deleting files in dataset '{dataset_id}' from bucket '{bucket_name}': {str(e)}"
        )


def main():
    """
    Top level function to execute sub-functions
    """
    parser = argparse.ArgumentParser(
        description="Delete V7 metadata files in a specified path within an S3 bucket when deleting a V7 item."
    )
    parser.add_argument("team_slug", help="the name of the S3 bucket")
    parser.add_argument("dataset_id", help="the name of the S3 bucket")
    parser.add_argument("item_name", help="the name of item to be deleted in V7")
    parser.add_argument("--s3_path", help="path to original s3 item")

    args = parser.parse_args()

    s3_client = boto3.client(
        "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
    )
    if args.s3_path:
        path = v7_prefix + "/" + args.s3_path + "/data/" + args.item_name
    else:
        path = v7_prefix + "/data/" + args.item_name

    delete_s3_files_in_path(bucket_name, path, s3_client)
    delete_v7_file(args.item_name, args.team_slug, args.dataset_id, s3_client)


if __name__ == "__main__":
    main()
