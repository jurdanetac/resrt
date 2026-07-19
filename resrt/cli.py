#!/usr/bin/python3

import re
import sys

from difflib import SequenceMatcher
from pathlib import Path

TOLERANCE = 0.75
MP4_SUFFIX = ".mp4"
SRT_SUFFIX = ".srt"


# Escape codes for colors in terminal, must be terminated with ENDC
class bcolors:
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


def clean_filename(filename: str) -> str | None:
    """Pre-processes media filenames for comparison by isolating the title text.

    Strips the file extension, standardizes punctuation separators into clean
    spaces, and removes common scene release metadata (codecs, resolutions,
    and source groups) using precise word boundaries.

    Args:
        filename: The raw file string to clean (e.g., 'The_Matrix_1080p.mp4').

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
    filename = filename.rsplit(".", 1)[0]

    # Replace common separators such as dots, underscores, and dashes with spaces
    filename = re.sub(r"[\._\-]", " ", filename)

    # Remove common tags, resolutions, and codecs if they are standalone words
    # This handles 1080p, 4k, x264, h264, BluRay, HDR, WEBRip, Atmos, etc.
    noise_pattern = r"\b(1080p|720p|2160p|4k|x264|h264|x265|h265|hevc|bluray|brrip|webrip|web dl|hdrip|dvdrip|dd5 1|atmos|dts|aac|aac2 0|xvid)\b"
    filename = re.sub(noise_pattern, "", filename, flags=re.IGNORECASE)

    # Clean up extra whitespaces and lowercase the string
    filename = re.sub(r"\s+", " ", filename).strip().lower()

    return filename


def walk_directory(directory: Path) -> None:
    """Recursively traverses a directory tree using Pre-order DFS."""

    print(f"{bcolors.HEADER}{directory}/{bcolors.ENDC}")

    for path in directory.iterdir():
        if not path.exists():
            print(f"{bcolors.WARNING}Path does not exist: {path}{bcolors.ENDC}")
            continue

        # Ignore hidden
        elif path.name.startswith("."):
            continue

        # Subdirectory: dive deep instantly (DFS branch)
        elif path.is_dir():
            walk_directory(path)

        # File: Process file
        elif path.is_file():
            # mp4 detected, check if there's an srt for it in cwd
            if path.suffix == MP4_SUFFIX:
                cleaned_mp4_name = clean_filename(path.name)
                if not cleaned_mp4_name:
                    continue

                srt_list = [f for f in list(directory.iterdir()) if f.suffix == ".srt"]
                for srt in srt_list:
                    cleaned_srt_name = clean_filename(srt.name)

                    if not cleaned_srt_name:
                        continue
                    elif cleaned_srt_name == cleaned_mp4_name:
                        print(
                            f"{path.name}: {bcolors.BOLD}{bcolors.OKGREEN}OK{bcolors.ENDC}{bcolors.ENDC}"
                        )
                        break

                    # check if this srt name matches the mp4 name
                    similarity = compute_str_similarity(
                        cleaned_mp4_name, cleaned_srt_name
                    )
                    similarity = round(similarity, 4)

                    # match
                    if similarity >= TOLERANCE:
                        print()
                        print(f"MP4: {path.name} | {cleaned_mp4_name}")
                        print(f"SRT: {srt.name} | {cleaned_srt_name}")
                        print(f"{similarity*100:.2f}% match")

                        # ask user whether this srt is the one
                        pair = None
                        while not type(pair) == bool:
                            should_pair = input(f"pair? [y/n]: ").strip().lower()

                            if should_pair == "y":
                                pair = True
                            elif should_pair == "n":
                                pair = False
                                print()
                            else:
                                print(
                                    f"{bcolors.BOLD}{bcolors.FAIL}Invalid choice.{bcolors.ENDC}{bcolors.ENDC}"
                                )

                        if pair:
                            new_srt_filename = path.name.replace(MP4_SUFFIX, SRT_SUFFIX)
                            new_srt_path = srt.parent / new_srt_filename
                            # srt.rename(new_srt_path)
                            print(f"{srt.name} renamed to {new_srt_filename}")
                            print()
                            break

        else:
            # special system file (symlink, socket, device, etc.)
            continue


if __name__ == "__main__":
    try:
        args = sys.argv[1:]

        if not args:
            print("USAGE: python3 main.py /some/path/")
            sys.exit(1)

        directory = Path(sys.argv[1])
        walk_directory(directory)
    except KeyboardInterrupt as e:
        print()
        sys.exit(0)
