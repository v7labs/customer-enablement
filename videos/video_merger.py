"""
# Script name: video_merger.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Merges all .mp4 videos in a specified directory into a single video file

USAGE
python video_merger.py [-h] --dir DIRECTORY

REQUIRED ARGUMENTS
--dir DIRECTORY     Specify the directory containing the videos to be merged

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import argparse
from pathlib import Path
from typing import List
from moviepy.editor import VideoFileClip, concatenate_videoclips


def create_video_list(directory: Path) -> List[str]:
    """
    Creates a list of .mp4 video files in the specified directory.

    Parameters
    ----------
        directory (Path): The directory containing the videos

    Returns
    -------
        video_list (List[str]): List of video file paths
    """
    video_list = [str(path) for path in directory.glob("*.mp4")]
    return sorted(video_list)


def merge_videos(video_list: List[str]) -> None:
    """
    Merges the videos in the list and writes the output to a file.

    Parameters
    ----------
        video_list (List[str]): List of video file paths
    """
    new_video_list = [VideoFileClip(vid) for vid in video_list]
    final_clip = concatenate_videoclips(new_video_list)
    final_clip.write_videofile("merged-video-file.mp4")


def main():
    parser = argparse.ArgumentParser(description="Merge videos in a directory.")
    parser.add_argument(
        "--dir",
        type=Path,
        required=True,
        help="Directory containing the videos to be merged",
    )
    args = parser.parse_args()

    video_list = create_video_list(args.dir)
    merge_videos(video_list)


if __name__ == "__main__":
    main()
