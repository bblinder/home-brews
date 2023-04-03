#!/usr/bin/env python3

"""
CLI utility to convert text to uppercase and/or add spaces, a la "Strange World".

Accepts input text from stdin or as a positional argument.

Usage:
    your_script.py [-u] [-s] [text]

Arguments:
    text            The text to be processed. If not provided, the script reads from stdin.
    -u, --uppercase Convert the text to uppercase.
    -s, --spaces    Add spaces between characters in the text.

Example:
    echo "example text" | ./your_script.py -u -s
    Output: "E X A M P L E   T E X T"
"""


import argparse
import select
import sys


def add_spaces(text):
    """Add spaces between characters in a string."""
    spaced_text = " ".join(text)
    return spaced_text


def convert_to_uppercase(text):
    """Convert a string to uppercase."""
    upper_text = text.upper()
    return upper_text


def main():
    """Deciding whether to use stdin or a positional argument,
    and then passing the text to the appropriate functions."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "text",
        help="text to convert (default: read from stdin)",
        nargs="?",
        default=sys.stdin,
    )
    parser.add_argument(
        "-u", "--uppercase", help="convert to uppercase", action="store_true"
    )
    parser.add_argument(
        "-s", "--spaces", help="add spaces between characters", action="store_true"
    )
    args = parser.parse_args()

    if args.text == sys.stdin:
        # check if stdin is empty
        stdin_ready, _, _ = select.select([sys.stdin], [], [], 0)
        if stdin_ready:
            text = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)
    else:
        text = args.text

    if args.uppercase:
        text = convert_to_uppercase(text)

    if args.spaces:
        text = add_spaces(text)

    if not args.uppercase and not args.spaces:
        text = add_spaces(text)

    print(text)


if __name__ == "__main__":
    main()
