"""
# Script name: upload_item_with_tag.py
# Last edited: 07.01.24

DESCRIPTION
When executed from the command line, this script:
1: Uploads a file to a specified dataset in a Darwin team with a specified tag.

USAGE
python3 upload_item_with_tag.py [-h] api_key team_slug dataset_slug file_path tag

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
team_slug: The slug for your team
dataset_slug: The slug for your dataset
file_path: The path to the file you want to upload
tag: The tag you want to add to the file

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
from darwin.client import Client
from darwin.dataset.upload_manager import LocalFile, UploadHandler


def get_args() -> argparse.Namespace:
    """
    Parse and return command line arguments.

    Returns
    -------
        args (argparse.Namespace): API key, team slug, dataset slug, data directory, file name, tag
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("api_key", help="API key for authentication with Darwin")
    parser.add_argument("team_slug", help="Team slug for your Darwin team")
    parser.add_argument("dataset_slug", help="Dataset slug for your Darwin dataset")
    parser.add_argument("file_path", help="The path to the file you want to upload")
    parser.add_argument("tag", help="The tag you want to add to the file")
    return parser.parse_args()


def main() -> None:
    """
    Top level function to execute sub-functions.
    """
    args = get_args()

    # Initialize the V7 Darwin Client and RemoteDataset objects.
    client = Client.local()
    dataset = client.get_remote_dataset(f"{args.team_slug}/{args.dataset_slug}")

    local_files = [LocalFile(args.file_path, path="/", tags=[args.tag])]

    # Upload your files to your remote dataset.
    upload_handler = UploadHandler.build(dataset, local_files)
    upload_handler.upload()
    if upload_handler.errors:
        print(upload_handler.errors)


if __name__ == "__main__":
    main()
