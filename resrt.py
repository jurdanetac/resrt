#!/usr/bin/python3

import re
import sys

from pathlib import Path

from Levenshtein import ratio

TOLERANCE = 0.65


def extract_name_from_filename(file: Path) -> str | None:
    # look up year in filename
    filename = file.name
    regex = re.search("[0-9][0-9][0-9][0-9]", filename)
    if not regex:
        return None
    span_start, span_end = regex.span()
    # take the filename until the start of the year
    name = filename[: span_start - 1]
    return name.strip()


def walk_directory(directory: Path) -> None:
    for path in list(directory.iterdir()):
        if not path.exists():
            print(f"Path does not exist: {path}")
            continue

        # hidden
        if path.name.startswith("."):
            continue

        # subdirectory, use recursion
        elif path.is_dir():
            walk_directory(path)

        # actual file
        elif path.is_file():
            # mp4 detected, check if there's an srt for it in cwd
            if path.suffix == ".mp4":
                mp4_name = extract_name_from_filename(path)
                if not mp4_name:
                    continue

                srt_list = [f for f in list(directory.iterdir()) if f.suffix == ".srt"]
                for srt in srt_list:
                    srt_name = extract_name_from_filename(srt)

                    if not srt_name:
                        continue
                    elif srt_name == mp4_name:
                        print()
                        print(f"{directory}/{path.name}: OK")
                        break

                    # check if this srt name matches the mp4 name
                    similarity = ratio(mp4_name, srt_name)
                    similarity = round(similarity, 4)

                    # match
                    if similarity >= TOLERANCE:
                        print(f"{directory}/")
                        print(f"MP4: {path.name}")
                        print(f"SRT: {srt.name}")
                        print(f"{similarity*100}% match")

                        # ask user whether this srt is the one
                        pair = None
                        while not type(pair) == bool:
                            should_pair = input(f"pair? [y/n]: ").strip().lower()

                            if should_pair == "y":
                                pair = True
                            elif should_pair == "n":
                                pair = False
                            else:
                                print("Invalid choice.")

                        if pair:
                            old_srt_path = srt
                            new_srt_filename = path.name.replace(".mp4", ".srt")
                            new_srt_path = srt.parent / new_srt_filename
                            srt.rename(new_srt_path)
                            print(f"{old_srt_path} renamed to {new_srt_path}")

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
