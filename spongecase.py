#!/usr/bin/env python3

""" Spongecase: script to randomly change letters to caps or lowercase """

import argparse
import random
import select
import sys


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


def spongecase(text):
    """Randomly change letters to caps or lowercase"""
    output = ""
    for char in text:
        if random.randint(0, 1) == 1:
            output += char.upper()
        else:
            output += char.lower()

    return output


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Spongecase: script to randomly change letters to caps or lowercase"
    )
    parser.add_argument("text", help="Text to spongecase", default=sys.stdin, nargs="?")
    args = parser.parse_args()

    text = read_input(args, parser)
    print(spongecase(text))


if __name__ == "__main__":
    main()
