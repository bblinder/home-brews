#!/usr/bin/env python3

"""
CLI utility to convert text to uppercase and/or add spaces, a la "Strange World".

Accepts input text from stdin or as a positional argument.

Usage:
    strange_world_spaces.py [-u] [-s] [text]

Arguments:
    text            The text to be processed. If not provided, the script reads from stdin.
    -u, --uppercase Convert the text to uppercase.
    -s, --spaces    Add spaces between characters in the text.

Example:
    echo "example text" | ./strange_world_spaces.py -u -s
    Output: "E X A M P L E   T E X T"
"""


import argparse
import select
import sys


def add_spaces(text):
    """Add spaces between characters in a string."""
    return " ".join(text)


def convert_to_uppercase(text):
    """Convert a string to uppercase."""
    return text.upper()


def read_input(args, parser):
    """Read input from stdin or a positional argument."""
    if args.text == sys.stdin:
        # check if stdin is empty
        stdin_ready, _, _ = select.select([sys.stdin], [], [], 0)
        if stdin_ready:
            return sys.stdin.read().strip()

        parser.print_help()
        sys.exit(1)

    return args.text


def process_text(text, args):
    """Process the text according to the arguments."""
    if args.uppercase:
        text = convert_to_uppercase(text)

    if args.spaces:
        text = add_spaces(text)

    if not args.uppercase and not args.spaces:
        text = add_spaces(text)

    return text


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

    text = read_input(args, parser)
    processed_text = process_text(text, args)
    print(processed_text)


if __name__ == "__main__":
    main()
