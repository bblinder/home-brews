#!/usr/bin/env python3

import sys

import requests
import validators

try:
    import pyperclip as pc
except ImportError:
    print("::: Pyperclip module not found.")
    sys.exit(1)


def validate_url(url):
    if not validators.url(url):
        print(f"::: '{url}' is not a valid URL.")
        sys.exit(1)


# Follow URL redirect, print any hops along the way
def follow_redirect():
    # By default, whatever's currently in the clipboard gets pasted.
    if args.url:
        input = args.url
        validate_url(input)
    else:
        input = pc.paste()
        validate_url(input)
    r = requests.get(input, allow_redirects=True, timeout=5)

    if r.history:
        print(r.history)
    return r.url


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Follows URL redirects and returns a final address"
    )
    parser.add_argument(
        "-u",
        "--url",
        help="the URL to follow. By default, whatever's currently in the clipboard gets pasted.\
            Use '-u' to specify a URL manually.",
        required=False,
    )
    args = parser.parse_args()
    url = args.url

    # Copies the output to the system clipboard.
    output = follow_redirect()
    print(output)
    pc.copy(output)
