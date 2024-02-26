"""
# Script name: byom_validator.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Validates a JSON response against the V7 bring your own model (BYOM) JSON schema.

USAGE
Populate the json_data dictionary with your model's inference response and run:
python byom_validator.py [-h] --schema_path SCHEMA_PATH

REQUIRED ARGUMENTS
--schema_path SCHEMA_PATH   Path to V7 BYOM schema file

OPTIONAL ARGUMENTS
-h, --help                  Print the help message for the function and exit
"""

import sys
import json
import argparse
from jsonschema import validate, exceptions

# Define your JSON data here
JSON_DATA = {
    # Your JSON data
}


def validate_json(schema_path: str, json_data: dict) -> None:
    """
    Validates a JSON response against the V7 bring your own model (BYOM) JSON schema.

    Parameters
    ----------
        schema_path (str): Path to V7 BYOM schema file
        json_data (dict): Full inference response in JSON from your model

    Raises
    ------
        SystemExit: If validation fails, the program will exit with an error message

    Returns
    -------
        None
    """
    with open(schema_path) as f:
        json_schema = json.load(f)

    try:
        validate(instance=json_data, schema=json_schema)
    except exceptions.ValidationError as e:
        sys.exit(f"Validation failed with the following error:\n{e}")

    print("Validation succeeded!")


def main():
    parser = argparse.ArgumentParser(
        description="Validate a JSON response against the V7 BYOM JSON schema."
    )
    parser.add_argument(
        "--schema_path", type=str, required=True, help="Path to V7 BYOM schema file"
    )
    args = parser.parse_args()

    validate_json(args.schema_path, JSON_DATA)


if __name__ == "__main__":
    main()
