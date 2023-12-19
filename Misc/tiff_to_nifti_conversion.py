'''
# Script name: tiff_to_nifti_conversion.py
# Last edited: 28.11.23

DESCRIPTION
When executed from the command line, this script:
- 1: Take an existing tiff file and convert it to a nifti file
- 2: Save the newly generated nifti file

USAGE
python3 tiff_to_nifti_conversion.py [-h] tiff_path nifti_path

REQUIRED ARGUMENTS
tiff_path: path where the tiff file exists
nifti_path: path to save the nifti file

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
'''

import tifffile
import nibabel as nib
import numpy as np
import argparse


def get_args() -> argparse.Namespace:
    '''
    Parse and return command line arguments.

    Returns
    -------
        args (argparse.Namespace): API key, output directory and filename
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'tiff_path',
        help='path where the tiff file exists'
    )
    parser.add_argument(
        'nifti_path',
        help='path to save the nifti file'
    )
    return parser.parse_args()

def main() -> None:
    '''
    Top level function to execute sub-functions.
    '''
    # Parse and validate command line arguments
    args = get_args()

    # Load the TIFF image stack
    tiff_stack = tifffile.imread(args.tiff_path)

    # Create a NIfTI image object
    nifti_image = nib.Nifti1Image(tiff_stack, affine=np.eye(4))

    # Save the NIfTI image to a file
    nib.save(nifti_image, args.nifti_path)

if __name__ == '__main__':
    main()