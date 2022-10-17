#!/usr/bin/env python3

""" Spongecase: script to randomly change letters to caps or lowercase """

import argparse
import random


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Spongecase: script to randomly change letters to caps or lowercase"
    )
    parser.add_argument("text", help="Text to spongecase", type=str)
    args = parser.parse_args()

    user_input = args.text

    output = ""
    for char in user_input:
        if random.randint(0, 1) == 1:
            output += char.upper()
        else:
            output += char.lower()

    print(output)


if __name__ == "__main__":
    main()
