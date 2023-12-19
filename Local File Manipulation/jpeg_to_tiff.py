'''
# Script name: jpeg_to_tiff.py
# Last edited: 21.11.23

DESCRIPTION
When executed from the command line, this script:
- 1: Takes a jpeg file located locally
- 2: Converts to Tiff and saves locally
- 3: Uploads the converted file to a specified dataset in Darwin

USAGE
python3 jpeg_to_tiff.py [-h] api_key dataset_slug source_folder_path target_folder_path

REQUIRED ARGUMENTS
api_key: V7 Darwin API key for your team
dataset_slug: slugified version of the dataset name
source_folder_path: path to files for conversion
target_folder_path: path to destination folder


OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''


from PIL import Image
from darwin.client import Client
import os
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
        'dataset_slug',
        help='slugified version of the dataset name'
    )
    parser.add_argument(
        'source_folder_path',
        help='path to files for conversion'
    )
    parser.add_argument(
        'target_folder_path',
        help='path to destination folder'
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


def get_filepaths(source_folder_path):
    return [os.path.join(source_folder_path, file) for file in os.listdir(source_folder_path) if not file.startswith('.')]

def convert_and_save(filepaths,target_folder_path):
    print(f"Beginning conversion of {len(filepaths)} files...")
    for filepath in filepaths:
        # Open each image, convert it to an RGB format, then save as .tif
        filename = filepath.split('/')[-1]
        print(f"Converting {filename}...")
        image = Image.open(filepath)
        image.save(os.path.join(target_folder_path, filename.split('.')[0] + '.tif'))
    print(f"Converted {len(filepaths)} files.")

def upload_to_dataset(ApiKey,dataset_slug,target_folder_path):
    client = Client.from_api_key(ApiKey)
    dataset = client.get_remote_dataset(dataset_slug)
    local_files = [os.path.join(target_folder_path, file) for file in os.listdir(target_folder_path) if not file.startswith('.')]
    print(f"Uploading {len(local_files)} files...")
    upload = dataset.push(files_to_upload=local_files)
    print("Done!")

def main():
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()
    validate_api_key(args.api_key)

    filepaths = get_filepaths(args.source_folder_path)
    convert_and_save(filepaths,args.target_folder_path)
    upload_to_dataset(args.api_key,args.dataset_slug,args.target_folder_path)

if __name__ == "__main__":
    main()
