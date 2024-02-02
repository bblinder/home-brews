#!/usr/bin/env python3

"""
Using the Ollama python lib to chat with the model.
"""

import os
import sys
import argparse
import ollama


def read_input(input_file):
    """
    Read the content of the input file.

    Args:
        input_file (str): The path to the input file.

    Returns:
        str: The content of the input file.

    Raises:
        FileNotFoundError: If the input file does not exist.
    """
    if input_file and os.path.exists(input_file):
        with open(input_file, "r") as f:
            return f.read()
    elif input_file:
        print(f"File {input_file} does not exist")
        sys.exit(1)
    else:
        return None
        # return sys.stdin.read()


def generate_response(prompt):
    """
    Generate a response using the Ollama chat model.

    Args:
        prompt (str): The user's prompt.

    Returns:
        str: The generated response.
    """
    response = ollama.chat(
        model="llama2:13b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response["message"]["content"]


def main():
    """Making sense of the args."""

    args = argparse.ArgumentParser()
    args.add_argument("--prompt", help="Prompt to pass to Ollama", required=True)
    args.add_argument("--input_file", help="Input file", default=None)
    args = args.parse_args()

    prompt = args.prompt

    if args.input_file:
        file_content = read_input(args.input_file)
        if file_content is not None:
            prompt = file_content

    response = generate_response(prompt)
    print(response)


if __name__ == "__main__":
    main()
