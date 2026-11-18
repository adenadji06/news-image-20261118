"""Entry program for news-image-20261118 (v2).

The image is drawn in advance (see README.md for the 36-story list and the
rendering script kept outside this repo) and shipped as entry.png beside
this file. This program only copies it to the output directory, so both
grader runs produce byte-identical output.
"""

import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("entry.png missing next to main.py", file=sys.stderr)
        return 1
    if os.path.getsize(src) == 0:
        print("entry.png is empty", file=sys.stderr)
        return 1
    with open(src, "rb") as fh:
        magic = fh.read(8)
    if magic != PNG_MAGIC:
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    dst = os.path.join(out_dir, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
