#!/usr/bin/env python3

"""Generate a haiku based on the current time."""

import datetime
import subprocess
import shlex
import argparse


DEFAULT_SUMMARIZATION_PROMPT = "[INST]Generate a haiku based on the following time:"
CHAR_COUNT = 6700  # We don't want to exceed Mistral's 7,000 token context size.
TEMPERATURE = 1
NUM_TOKENS = 500


def get_current_time():
    """Get the current time."""
    current_time = datetime.datetime.now().time()
    return current_time


def generate_haiku(
    text, llamafile_path, summarization_prompt=DEFAULT_SUMMARIZATION_PROMPT
):
    """Invoking the llamafile"""
    escaped_text = shlex.quote(f"{summarization_prompt} {text} [/INST]")
    cmd = f"echo {escaped_text} | {llamafile_path} -c {CHAR_COUNT} -f /dev/stdin --temp {TEMPERATURE} -n {NUM_TOKENS} --silent-prompt"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error in llamafile execution: {e}")
        return ""


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate a haiku based on the current time."
    )
    parser.add_argument("llamafile_path", help="Path to llamafile binary")

    args = parser.parse_args()
    llamafile_path = args.llamafile_path
    current_time = get_current_time()
    haiku = generate_haiku(current_time, llamafile_path)
    print(haiku)


if __name__ == "__main__":
    main()
