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
from tqdm import tqdm

SUPPORTED_MODELS = ["mistral", "llama2:13b"]
DEFAULT_TEMP = 0.0


def read_input(input_path):
    """Read the content of the input file, with support for PDFs."""
    file_extension = os.path.splitext(input_path)[1].lower()

    if file_extension == ".pdf":
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(input_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except ImportError:
            print("PyMuPDF (fitz) is required to read PDF files.")
            sys.exit(1)
    elif os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print(f"File {input_path} does not exist")
        sys.exit(1)


def generate_response(prompt, model):
    """Generate a response using the selected model."""
    response = ollama.chat(
        model=model,
        options={"temperature": DEFAULT_TEMP},
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


def process_inputs(base_prompt, inputs, model):
    """Combine base prompt with content from inputs to generate responses."""
    responses = []
    if inputs:  # Check if input files are provided
        for input_source in tqdm(inputs, desc="Processing inputs"):
            content = read_input(input_source)
            combined_prompt = f"{base_prompt} {content}".strip()
            response = generate_response(combined_prompt, model)
            responses.append(response)
    else:  # If no input files, use just the base prompt
        response = generate_response(base_prompt, model)
        responses.append(response)
    return responses


def write_output(output_file, responses):
    """Write the responses to the output file or print to stdout."""
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            for response in responses:
                f.write(response + "\n\n")
    else:
        for response in responses:
            print(response + "\n")


def main():
    """Making sense of the args."""
    args = argparse.ArgumentParser()
    args.add_argument("-p", "--prompt", help="Base prompt", required=True)
    args.add_argument(
        "-i", "--inputs", nargs="*", help="Paths to input files", default=[]
    )
    args.add_argument(
        "-m",
        "--model",
        choices=SUPPORTED_MODELS,
        help="Model to use",
        default="mistral",
    )
    args.add_argument("-o", "--output", help="Output file", default=None)
    args.add_argument("-t", "--temperature", help="Temperature", default=DEFAULT_TEMP)
    args = args.parse_args()

    responses = process_inputs(args.prompt, args.inputs, args.model)
    write_output(args.output, responses)


if __name__ == "__main__":
    main()
