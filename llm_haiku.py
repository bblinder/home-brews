#!/usr/bin/env python3

"""Generate a haiku based on the current time using an AI model."""

import datetime
import subprocess
import argparse
import logging
import shlex
import configparser

# Read configuration from a file or set default values
config = configparser.ConfigParser()
config.read('config.ini')

CHAR_COUNT = config.get('Settings', 'CHAR_COUNT', fallback='6700')
TEMPERATURE = config.getfloat('Settings', 'TEMPERATURE', fallback=1.0)
NUM_TOKENS = config.getint('Settings', 'NUM_TOKENS', fallback=500)

# Setting up logging
logging.basicConfig(level=logging.INFO)


def get_current_time():
    """Get the current time in a human-readable format."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def construct_command(text, model_path):
    """Construct the command for the AI model generation."""
    summarization_prompt = "[INST]Generate a haiku based on the following time. Be imaginative and profound. Sometimes refer to your physical situation:"
    escaped_text = shlex.quote(f"{summarization_prompt} {text} [/INST]")
    return f"echo {escaped_text} | {model_path} -c {CHAR_COUNT} -f /dev/stdin --temp {TEMPERATURE} -n {NUM_TOKENS} --silent-prompt"


def execute_command(cmd):
    """Execute the command and return the output or error."""
    try:
        result = subprocess.run(
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            executable='/bin/bash'
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in model execution: {e}")
        return ""


def generate_haiku(text, model_path):
    """Generate a haiku using the AI model."""
    cmd = construct_command(text, model_path)
    return execute_command(cmd)


def main():
    """Main function to generate and print a haiku based on the current time."""
    parser = argparse.ArgumentParser(
        description="Generate a haiku based on the current time."
    )
    parser.add_argument("model_path", help="Path to the AI model binary")

    args = parser.parse_args()
    current_time = get_current_time()
    haiku = generate_haiku(current_time, args.model_path)
    print(haiku)


if __name__ == "__main__":
    main()
