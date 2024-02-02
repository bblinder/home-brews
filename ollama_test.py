#!/usr/bin/env python3

"""
Using the Ollama python lib to chat with supported models.

TODO:
- [] Add URL summarization
- [] Replace print statements with logging
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

    if not input_file or not os.path.exists(input_file):
        print(f"File {input_file} does not exist")
        sys.exit(1)

    file_extension = os.path.splitext(input_file)[1].lower()

    # For PDF files
    if file_extension == ".pdf":
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(input_file)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except ImportError:
            print("PyMuPDF (fitz) is required to read PDF files.")
            sys.exit(1)

    # For Markdown or plain text files
    else:
        with open(input_file, "r", encoding="utf-8") as f:
            return f.read()


def generate_response(prompt, model):
    """
    Generate a response using the selected model.
    """
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return response["message"]["content"]


def write_output(output_file, content):
    """
    Write the content to the output file.
    """
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(content)


SUPPORTED_MODELS = ["mistral", "llama2:13b"]


def main():
    """Making sense of the args."""

    args = argparse.ArgumentParser()
    args.add_argument("-p", "--prompt", help="Prompt to pass to Ollama", required=True)
    args.add_argument("-i", "--input_file", help="Input file", default=None)
    args.add_argument(
        "-m",
        "--model",
        choices=SUPPORTED_MODELS,
        help="Model to use",
        default="mistral",
    )
    args.add_argument("-o", "--output", help="Output file", default=None)
    args = args.parse_args()

    prompt = args.prompt
    model = args.model

    if args.input_file:
        file_content = read_input(args.input_file)
        if file_content is not None:
            prompt = file_content

    print("Using model:", model)
    response = generate_response(prompt, model)
    write_output(args.output, response)


if __name__ == "__main__":
    main()
