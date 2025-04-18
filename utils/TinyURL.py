#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pyperclip"]
# ///

"""Use the tinyURL API to shorten URLs."""

import argparse
import contextlib
import sys
from urllib.parse import urlencode

import requests

try:
    import pyperclip as pc
except ImportError:
    print("::: Pyperclip not installed, copying to clipboard will not work.")
    print("::: Install with `pip install pyperclip`")
    print("::: Continuing without pyperclip...\n")
    pc = None

argparser = argparse.ArgumentParser(description="Shorten URLs with the TinyURL API.")
argparser.add_argument("urls", metavar="URL", nargs="+", help="URLs to shorten")
args = argparser.parse_args()


def make_tiny(url):
    """Return a tiny version of the given URL."""
    request_url = "http://tinyurl.com/api-create.php?" + urlencode({"url": url})
    with contextlib.closing(requests.get(request_url, timeout=5)) as response:
        return response.text


def main():
    """Run the main program."""
    for tinyurl in map(make_tiny, sys.argv[1:]):
        print(tinyurl)
        if pc:
            pc.copy(tinyurl)


if __name__ == "__main__":
    main()
