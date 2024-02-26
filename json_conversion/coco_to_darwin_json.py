"""
# Script name: coco-to-darwin-json.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Converts Coco JSON data to Darwin JSON format

USAGE
python coco-to-darwin-json.py [-h] ...

REQUIRED ARGUMENTS [if any]

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

from typing import Dict, Any
from darwin.importer.formats import coco
import json

COCO_JSON = "path/to/coco.json"


def get_coco_data(coco_json: str) -> Dict[str, Any]:
    """
    Gets Coco JSON data

    Parameters
    ----------
        coco_json (str): Path to the Coco JSON file

    Returns
    -------
        coco_data (Dict[str, Any]): The loaded Coco JSON data
    """
    with open(coco_json) as f:
        return json.load(f)


def convert_to_darwin_json(coco_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts Coco JSON data to Darwin JSON format

    Parameters
    ----------
        coco_data (Dict[str, Any]): The loaded Coco JSON data

    Returns
    -------
        v2_darwin_json (Dict[str, Any]): The converted Darwin JSON data
    """
    category_lookup_table = {
        category["id"]: category for category in coco_data["categories"]
    }
    dar_json = coco.parse_annotation(coco_data["annotations"][0], category_lookup_table)
    return {"paths": [dar_json.data["path"]]}


def main():
    coco_data = get_coco_data(COCO_JSON)
    v2_darwin_json = convert_to_darwin_json(coco_data)
    print(v2_darwin_json)


if __name__ == "__main__":
    main()
