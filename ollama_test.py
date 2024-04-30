#!/usr/bin/env python3

"""
Using the Ollama python lib to chat with supported models.

TODO:
- [] Add URL summarization
- [] Replace print statements with logging
"""

import sys
import platform
import pathlib
import argparse
import subprocess
from time import sleep
import ollama
from tqdm import tqdm

SUPPORTED_MODELS = ["mistral", "llama3:8b"]
DEFAULT_TEMP = 0.0


def read_input(input_path):
    """Read the input file and return the content. Support for PDFs"""
    file_extension = pathlib.Path(input_path).suffix.lower()
    if file_extension == ".pdf":
        try:
            import fitz
            doc = fitz.open(input_path)
            text = "".join([page.get_text() for page in doc])
            return text
        except ImportError as e:
            raise SystemExit("Error: PyMuPDF (fitz) is required to read PDF files. Install it via pip.") from e
    elif pathlib.Path(input_path).exists():
        with open(input_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise FileNotFoundError(f"Error: File {input_path} does not exist.")


def generate_response(prompt, model):
    """Generate a response using the selected model."""
    try:
        response = ollama.chat(
            model=model,
            options={"temperature": DEFAULT_TEMP},
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"Failed to generate response: {e}")
        sys.exit(1)


def process_inputs(base_prompt, inputs, model):
    """Combine base prompt with content from inputs to generate responses."""
    responses = []
    if inputs:
        for input_source in tqdm(inputs, desc="Processing inputs"):
            content = read_input(input_source)
            combined_prompt = f"{base_prompt} {content}".strip()
            response = generate_response(combined_prompt, model)
            responses.append(response)
    else:
        response = generate_response(base_prompt, model)
        responses.append(response)
    return responses


def write_output(output_file, responses):
    """Write the responses to the output file or print to stdout."""
    try:
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                for response in responses:
                    f.write(response + "\n\n")
        else:
            for response in responses:
                print(response + "\n")
    except Exception as e:
        print(f"Failed to write output: {e}")
        sys.exit(1)


def is_application_open(app_name):
    """Check if the dependent app is running."""
    try:
        # Windows
        if platform.system() == "Windows":
            output = subprocess.check_output(["tasklist"], text=True)
        else:  # else assume Unix
            output = subprocess.check_output(["ps", "aux"], text=True)
        return any(app_name in line for line in output.splitlines())
    except subprocess.CalledProcessError as e:
        print(f"::: Error checking app status: {e}")
        sys.exit(1)


def main():
    """Main function."""
    try:
        responses = process_inputs(args.prompt, args.inputs, args.model)
        write_output(args.output, responses)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
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

    app_name = "Ollama"
    if not is_application_open(app_name):
        print(f"::: {app_name} not running")
        if platform.system() == "Darwin":
            print(f"::: Opening {app_name}...")
            subprocess.run(["open", "-a", app_name], check=True)
            sleep(5)  # Giving it a little time to start
    main()
