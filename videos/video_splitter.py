"""
# Script name: video_splitter.py
# Last edited: 26.02.24

DESCRIPTION
When executed from the command line, this script:
- 1: Splits a video into multiple clips based on the provided clip frame length.

USAGE
python video_splitter.py [-h] video_path clip_frame_length

REQUIRED ARGUMENTS
video_path          The path to the video file to be split.
clip_frame_length   The length of each clip in frames.

OPTIONAL ARGUMENTS
-h, --help          Print the help message for the function and exit
"""

import os
import cv2 as cv
import math
from pathlib import Path
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Split a video into multiple clips.")
    parser.add_argument(
        "video_path", type=str, help="The path to the video file to be split."
    )
    parser.add_argument(
        "clip_frame_length", type=int, help="The length of each clip in frames."
    )
    return parser.parse_args()


def split_video(video_path: str, clip_frame_length: int):
    """
    Split a video into multiple clips.

    Parameters
    ----------
        video_path (str): The path to the video file to be split.
        clip_frame_length (int): The length of each clip in frames.

    Raises
    ------
        FileNotFoundError: If the video file does not exist.
    """

    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"No such file: '{video_path}'")

    video = cv.VideoCapture(str(video_path))
    fps = int(video.get(cv.CAP_PROP_FPS))
    frame_count = video.get(cv.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps
    video.release()

    clip_length = round((clip_frame_length / frame_count) * duration, 0)
    total_clips = math.ceil(duration / clip_length)

    file_path = video_path.parent / "video_clips"
    file_name = video_path.stem
    file_type = video_path.suffix.lstrip(".")

    os.system(f"mkdir {file_path}")

    clip_start = 0
    for i in range(0, total_clips):
        command = (
            f"ffmpeg -ss {clip_start} -t {clip_length} -i {str(video_path)} "
            + f"-acodec copy -vcodec copy {file_path}/{file_name}_clip_{i+1}.{file_type}"
        )
        os.system(command)
        clip_start += clip_length


def main():
    args = parse_arguments()
    split_video(args.video_path, args.clip_frame_length)


if __name__ == "__main__":
    main()
