#!/usr/bin/python3

import re
import sys

from pprint import pprint

from difflib import SequenceMatcher
from pathlib import Path

TOLERANCE = 0.80
MP4 = ".mp4"
SRT = ".srt"

class bcolors:
    """Escape codes for colors in terminal, must be terminated with ENDC."""
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def compute_str_similarity(a: str, b: str) -> float:
    """Returns float percentage of similarity between str a and b."""

    return SequenceMatcher(isjunk=None, a=a, b=b).ratio()


def is_filetype(filetype: str, file: Path) -> bool:
    """Return bool indicating if file is of filetype by comparing its suffix."""
    return file.suffix.lower() == filetype.lower()


def clean_filename(file: Path) -> str:
    """Pre-processes media filenames for comparison by isolating the title text.

    Strips the file extension, standardizes punctuation separators into clean
    spaces, and removes common scene release metadata (codecs, resolutions,
    and source groups) using precise word boundaries.

    Args:
        file: The file 'Path' object

    Returns:
        A normalized, lowercase string containing only the essential elements
        of the title.

    Examples:
        >>> clean_filename("The.Matrix.1999.1080p.BluRay.x264.mp4")
        'the matrix 1999'

        >>> clean_filename("Stranger_Things_S04E07_720p_WEB-DL.mkv")
        'stranger things s04e07'

        >>> clean_filename("2001.A.Space.Odyssey.Bluray.srt")
        '2001 a space odyssey'
    """

    # Strip the extension from the filename
    filename = file.stem

    # Replace common separators such as dots, underscores, and dashes with spaces
    filename = re.sub(r"[\._\-]", " ", filename)

    # Remove common tags, resolutions, and codecs if they are standalone words
    # This handles 1080p, 4k, x264, h264, BluRay, HDR, WEBRip, Atmos, etc.
    noise_pattern = r"\b(1080p|720p|2160p|4k|x264|h264|x265|h265|hevc|bluray|brrip|webrip|web dl|hdrip|dvdrip|dd5 1|atmos|dts|aac|aac2 0|xvid)\b"
    filename = re.sub(noise_pattern, "", filename, flags=re.IGNORECASE)

    # Clean up extra whitespaces and lowercase the string
    filename = re.sub(r"\s+", " ", filename).strip().lower()

    return filename


if __name__ == "__main__":
    try:
        args = sys.argv[1:]

        if not args:
            print("USAGE: python3 main.py /some/path/")
            sys.exit(1)

        directory = Path(sys.argv[1])
        recursive_directory_paths = directory.rglob("*")
        directory_map = {}
        directory_map[directory] = { MP4: [], SRT: [] }  # init with provided dir

        # map all mp4 and srt in a python dictionary for less I/O and quicker access
        for path in recursive_directory_paths:
            # only consider regular files
            if not path.is_file():
                continue

            # reassign variables for better comprehension
            file = path
            file_dir = file.parent

            # create a key for the files in the file's directory if not present
            if file_dir not in directory_map:
                directory_map[file_dir] = {MP4: [], SRT: []}

            # append accordingly
            if is_filetype(MP4, file):
                directory_map[file_dir][MP4].append(file)
            elif is_filetype(SRT, file):
                directory_map[file_dir][SRT].append(file)

        # once all relevant paths are loaded into memory, check the mp4 files for relevant srt files
        for folder_path, buckets in directory_map.items():
            mp4_files = buckets[MP4]
            srt_files = buckets[SRT]

            # without suffixes
            existing_srt_stems = {srt.stem for srt in srt_files}

            # Check if it's already paired with a subtitle file
            for mp4 in mp4_files:
                if mp4.stem in existing_srt_stems:
                    print(f"{mp4.name}: {bcolors.BOLD}{bcolors.OKGREEN}OK{bcolors.ENDC}{bcolors.ENDC}")
                    continue

                mp4_cleaned_name = clean_filename(mp4)
                for srt in srt_files[:]:
                    srt_cleaned_name = clean_filename(srt)
                    similarity = compute_str_similarity(mp4_cleaned_name, srt_cleaned_name)

                    if similarity >= TOLERANCE:
                        color_to_show = bcolors.WARNING
                        if mp4_cleaned_name == srt_cleaned_name:
                            color_to_show = bcolors.OKGREEN

                        print()
                        print(f"MP4: {mp4.name}\t({color_to_show}{mp4_cleaned_name}{bcolors.ENDC})")
                        print(f"SRT: {srt.name}\t({color_to_show}{srt_cleaned_name}{bcolors.ENDC})")
                        print(f"{similarity*100:.2f}% match")

                        # ask user whether this srt is the one
                        should_pair = input(f"pair? [y/n]: ").strip().lower()

                        if should_pair == "y":
                            srt_previous_filename = srt.name
                            srt_new_filename = mp4.stem + SRT
                            srt_new_path = srt.parent / srt_new_filename
                            srt.rename(srt_new_path)
                            print(f"{srt_previous_filename} renamed to {srt_new_filename}")
                            print()

                            # remove srt from options
                            srt_files.remove(srt)

                            # update the set
                            existing_srt_stems.add(mp4.stem)

                            # skip other choices
                            break
                        elif should_pair == "n":
                            print()
                        else:
                            print(
                                f"{bcolors.BOLD}{bcolors.FAIL}Invalid choice.{bcolors.ENDC}{bcolors.ENDC}"
                            )
                            print()

    except KeyboardInterrupt as e:
        print()
        sys.exit(0)
