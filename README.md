# resrt 💬

> "Cut my files into pieces, this is my last resrt!"

`resrt` is a lightweight, recursive command-line tool designed to clean up chaotic media directories. If you have a downloads folder overflowing with horribly named `.mp4` video files and mismatched `.srt` subtitle files, `resrt` will walk your directories, fuzzy-match them using Levenshtein distance, and rename the subtitle files to match their corresponding videos perfectly.

---

## Features

* **Recursive Directory Walking:** Traverses nested folders to find unmatched files.
* **Smart Fuzzy Matching:** Uses the Levenshtein distance algorithm to recognize matches even when filenames are riddled with torrent clutter, release group tags, or slightly different punctuation.
* **Year Detection:** Automatically extracts titles by scanning for 4-digit years (e.g., `Movie.Name.2026.1080p.mp4` becomes `Movie.Name`).
* **Interactive Approvals:** Keeps you in control by prompting you to confirm matches before executing any rename commands.
* **Auto-Skip Already Match-Named Files:** Avoids prompting you for `.srt` files that already perfectly match their video counterpart.

---

## Installation

### 1. Clone or Download the Script
Save the script as `main.py` in your working folder.

### 2. Install Dependencies
`resrt` relies on the `Levenshtein` library to calculate the similarity between filenames. You can install it via `pip`:

```bash
pip install Levenshtein
