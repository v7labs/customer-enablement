'''
# Script name: modify_subannotation_name_and_order.py
# Last edited: 28.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Loads a JSON file containing subattributes
- 2: Removes part of the name of the attribute and switches ordering of the remaining name
- 3: Set Ocluded flag to true if any attributes with the given name exist
- 4: Saves modified JSON back to the file

USAGE
python3 modify_subannotation_name_and_order.py [-h] folder_path

REQUIRED ARGUMENTS
folder_path: Path containing JSON file

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

# Import json file
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
        'folder_path',
        help='Path containing JSON file'
    )
    return parser.parse_args()

def rename_and_modify_subattribute_name(data):
    '''
    Renames and modifies the name of the subattribute. 
    Sets a flag if the attributes exist and saves new file

    Parameters
    ----------
        data (json): The annotation data containing subattribute information

    '''
    new_attributes = []
    for attr in data['attributes']:
        # Remove 'invisible' from the name
        attr = attr.replace(' invisible', '')

        # Split the name into parts and switch the first and second part
        parts = attr.split()
        if len(parts) >= 2:
            parts[0], parts[1] = parts[1], parts[0]

        # Join the parts back into a single string
        new_attr = ' '.join(parts)
        new_attributes.append(new_attr)

    # Update the attributes with the modified list
    data['attributes'] = new_attributes

    # Iterate over the nodes in the skeleton
    for node in data['skeleton']['nodes']:
        # Check if the name of the node is in the attributes list
        if any(attr in node['name'] for attr in data['attributes']):
            # Set the occluded flag to true
            node['occluded'] = True

    # Save the modified JSON back to the file
    with open('fixed_annotation.json', 'w') as f:
        json.dump(data, f, indent=4)

def main() -> None:
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()

    # Load the JSON file
    with open(args.folder_path) as f:
        data = json.load(f)

    rename_and_modify_subattribute_name(data)

if __name__ == '__main__':
    main()