'''
# Script name: coco-to-darwin-json.py
# Last edited: 27.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Converts a coco file to darwin json format

USAGE
python3 coco-to-darwin-json.py [-h] coco_json_path

REQUIRED ARGUMENTS
coco_json_path: Path to coco json file

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

from darwin.importer.formats import coco
from darwin.client import Client
import json
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
        'coco_json_path',
        help='Path to coco json file'
    )

    return parser.parse_args()

def main() -> None:
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()

    client = Client.local()

    #Gets Coco JSON data
    f = open(args.coco_json_path)
    coco_data = json.load(f)

    #Defining category lookup
    category_lookup_table = {category["id"]: category for category in coco_data["categories"]}

    #Converts annotation data to Darwin JSON format
    dar_json = coco.parse_annotation(coco_data["annotations"][0],category_lookup_table)

    #Converts to Darwin JSON V2 format
    v2_darwin_json = {'paths':[dar_json.data['path']]}

    print(v2_darwin_json)


if __name__ == '__main__':
    main()