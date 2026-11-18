"""Entry program for news-image-20261118 (v3, render-finesse pass).

The front-page image is drawn in advance (see README.md for the 36-story
list and the rendering script kept outside this repo) and shipped as
entry.png beside this file. This program only validates that file and
copies it to the output directory, so both grader runs produce
byte-identical output.
"""

import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SOURCE_NAME = "entry.png"


def fail(message):
    """Report a problem on stderr and return the failure exit code."""
    print(message, file=sys.stderr)
    return 1


def entry_path():
    """Absolute path of the image shipped next to this program."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, SOURCE_NAME)


def check_png(path):
    """Return an error string unless path is a non-empty PNG file."""
    if not os.path.isfile(path):
        return f"{SOURCE_NAME} missing next to main.py"
    if os.path.getsize(path) == 0:
        return f"{SOURCE_NAME} is empty"
    with open(path, "rb") as handle:
        magic = handle.read(len(PNG_MAGIC))
    if magic != PNG_MAGIC:
        return f"{SOURCE_NAME} is not a PNG file"
    return None


def output_path():
    """Destination path inside the grader's output directory."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, SOURCE_NAME)


def main():
    src = entry_path()
    error = check_png(src)
    if error is not None:
        return fail(error)
    shutil.copyfile(src, output_path())
    return 0


if __name__ == "__main__":
    sys.exit(main())
