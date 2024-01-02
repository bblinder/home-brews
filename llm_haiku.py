#!/usr/bin/env python3

"""Generate a haiku based on the current time using a local LLM model."""

import datetime
import subprocess
import argparse
import logging
import shlex
import configparser

# Read configuration from a file or set default values
config = configparser.ConfigParser()
config.read("config.ini")

PROMPT = """[INST]Generate a very short one-stanza poem based on the following time, in a style similar to this example:
'In cozy shelves, I do reside, /
Its nearly noon, the clock confides.'
Be imaginative and profound, incorporating the time: """

CHAR_COUNT = config.get("Settings", "CHAR_COUNT", fallback="6700")
TEMPERATURE = config.getfloat("Settings", "TEMPERATURE", fallback=1.9)
NUM_TOKENS = config.getint("Settings", "NUM_TOKENS", fallback=500)

# Setting up logging
logging.basicConfig(level=logging.INFO)


def get_current_time():
    """Get the current time in a human-readable format, including AM/PM, and return both plain and formatted versions."""
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    # Format for bold and blue text (ANSI escape codes)
    formatted_time = f"\033[1;34m{time_str}\033[0m"
    return time_str, formatted_time


def construct_command(plain_text, formatted_text, model_path):
    """Construct the command for the LLM model generation, including the formatted time."""
    summarization_prompt = PROMPT + formatted_text
    escaped_text = shlex.quote(f"{summarization_prompt} [/INST]")
    return f"echo {escaped_text} | {model_path} -c {CHAR_COUNT} -f /dev/stdin --temp {TEMPERATURE} -n {NUM_TOKENS} --silent-prompt"


def execute_command(cmd):
    """Execute the command and return the output or error."""
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
        logging.error(f"Error in model execution: {e}")
        return ""


def generate_poem(plain_text, formatted_text, model_path):
    """Generate a short poem using the LLM model."""
    cmd = construct_command(plain_text, formatted_text, model_path)
    return execute_command(cmd)


def main():
    """Main function to generate and print a poem based on the current time."""
    parser = argparse.ArgumentParser(
        description="Generate a poem based on the current time."
    )
    parser.add_argument("model_path", help="Path to the LLM model binary")

    args = parser.parse_args()
    plain_time, formatted_time = get_current_time()
    poem = generate_poem(plain_time, formatted_time, args.model_path)
    # print(f"The current time is {formatted_time}.\nHere is your poem:\n{poem}")
    print(f"{poem}")


if __name__ == "__main__":
    main()
