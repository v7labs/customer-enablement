'''
# Script name: subattribute_percentage_perclass.py
# Last edited: 28.11.2023

DESCRIPTION
When executed from the command line, this script:
- 1: Loads all exported JSON files within a folder
- 2: For each file in the folder, computes the subattribute count per each class
- 3: Prints this for each class

USAGE
python3 subattribute_percentage_perclass.py [-h] folder_path

REQUIRED ARGUMENTS
folder_path: Folder containing json files

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

# Import json file
import json
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
        'folder_path',
        help='Folder containing json files'
    )
    return parser.parse_args()

def main() -> None:
    '''
    Top level function to execute.
    '''
    # Parse and validate command line arguments
    args = get_args()


    # Initiliase a count dict for class 
    counts = {}

    # Loop through each file in the folder
    for filename in os.listdir(args.folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(args.folder_path, filename)
            
            # Open and read the JSON file
            with open(file_path, "r") as file:
                json_data = json.load(file)

            # Iterate over the annotations
            for annotation in json_data['annotations']:
                # Get the class name
                class_name = annotation['name']

                # Get the subattributes
                subattributes = annotation['attributes']

                # Check if the class name is already in the counts dictionary
                if class_name not in counts:
                    counts[class_name] = {}

                # Iterate over the subattributes
                for subattribute in subattributes:
                    # Check if the subattribute is already in the counts dictionary
                    if subattribute not in counts[class_name]:
                        counts[class_name][subattribute] = 0

                    # Increment the count for the subattribute
                    counts[class_name][subattribute] += 1

    # Print the counts
    for class_name, subattribute_counts in counts.items():
        print(f'Class: {class_name}')
        for subattribute, count in subattribute_counts.items():
            print(f'{subattribute}: {count}')
        print()

if __name__ == '__main__':
    main()
