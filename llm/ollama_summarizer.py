#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "beautifulsoup4",
#     "ollama",
#     "requests",
#     "tqdm",
# ]
# ///

"""
Using the Ollama python lib to chat with supported models.

TODO:
- [x] Add URL summarization
- [x] Replace print statements with logging
- [x] Dynamically show available Ollama models
- [ ] Handle multiple inputs in the command line
"""

import sys
import os
import subprocess
import json
import platform
import pathlib
import argparse
import logging
import random
import re
import time
from time import sleep
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
import ollama
from tqdm import tqdm

if sys.version_info >= (3, 12):
    os.system("cls" if os.name == "nt" else "clear")  # Clear the terminal screen

DEFAULT_MODEL = "mistral-nemo:latest"
DEFAULT_TEMP = 0.0
TIMEOUT_SECONDS = 5
DEFAULT_PROMPT = "As a helpful assistant, your task is to provide a concise and precise summary of the given document. Focus on extracting the main points and relevant details from the text while maintaining brevity in your response. Ensure that your summary captures the essence of the conversation or discussion without sacrificing accuracy. Please note that you should be able to handle various types of documents, such as interviews, meetings, transcripts, or presentations. Your response should be flexible enough to allow for different topics and contexts while still providing a clear and focused summary."

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_available_models():
    """Get list of available models from Ollama."""
    try:
        # First try using the ollama Python client
        models_response = ollama.list()
        if isinstance(models_response, dict) and "models" in models_response:
            models = [model["name"] for model in models_response["models"]]
            return models

        # If the Python client doesn't work as expected, fallback to CLI
        else:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, check=True
            )

            # Parse the output manually since it's not in JSON format
            models = []
            for line in result.stdout.strip().split("\n"):
                # Skip the header line
                if line.startswith("NAME") or not line.strip():
                    continue

                # Extract the model name (first column before any whitespace)
                model_name = line.split()[0].strip()
                if model_name:
                    models.append(model_name)

            return models if models else ["mistral-nemo", "llama3"]
    except (subprocess.SubprocessError, KeyError, FileNotFoundError) as e:
        logging.warning(f"Could not retrieve model list: {str(e)}")
        # Return some default models if we can't get the actual list
        return ["mistral-nemo"]


def get_user_agent():
    """Get a random user agent from the list."""
    return random.choice(USER_AGENTS)


def is_valid_url(url):
    """Check if the URL is valid and follow redirects."""
    if pathlib.Path(url).exists():
        return False
    try:
        encoded_url = quote(url, safe=":/")
        response = requests.get(
            encoded_url, allow_redirects=True, timeout=TIMEOUT_SECONDS
        )
        return response.status_code < 400
    except requests.RequestException as e:
        logging.error("URL validation error: %s", str(e))
        return False


def get_text_from_url(url):
    """Scrape and process text from URL."""
    headers = {
        "User-Agent": get_user_agent(),
    }

    def fetch_url(fetch_url):
        try:
            response = requests.get(
                fetch_url,
                allow_redirects=True,
                timeout=TIMEOUT_SECONDS,
                headers=headers,
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text()
                return re.sub(r"[\s\xa0]+", " ", text).strip()
            return None
        except requests.RequestException:
            return None

    # Try fetching the URL directly
    text = fetch_url(url)
    return text


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
            logging.error(
                "Error: PyMuPDF (fitz) is required to read PDF files. "
                "Install it via pip."
            )
            raise SystemExit from e
    elif pathlib.Path(input_path).exists():
        with open(input_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise FileNotFoundError("Error: File %s does not exist." % input_path)


def generate_response(prompt, model):
    """Generate a response using the selected model."""
    try:
        # First measure token count estimate for progress display
        token_estimate = len(prompt.split()) // 4  # Rough estimate

        print(f"Sending prompt to {model}...")

        # Create a progress spinner while the model works
        with tqdm(
            total=None,
            desc="Model working",
            bar_format="{desc}: {elapsed}",
            leave=False,
        ) as pbar:
            # Setup progress tracking
            start_time = time.time()

            # Get response from model
            response = ollama.chat(
                model=model,
                options={"temperature": DEFAULT_TEMP},
                messages=[{"role": "user", "content": prompt}],
            )

            # Update progress bar until complete
            while (
                time.time() - start_time < 0.5
            ):  # Ensure bar displays for at least 0.5s
                pbar.update(1)
                time.sleep(0.1)

        # Show completion message
        response_text = response["message"]["content"]
        token_count = len(response_text.split())
        print(f"✓ Response generated: ~{token_count} tokens")

        return response_text
    except Exception as e:
        logging.error("Failed to generate response: %s", str(e))
        sys.exit(1)


def process_inputs(base_prompt, inputs, model):
    """Combine base prompt with content from inputs to generate responses."""
    responses = []

    if not inputs:
        # If no inputs, just process the base prompt
        with tqdm(total=1, desc="Generating response", unit="step") as pbar:
            response = generate_response(base_prompt, model)
            pbar.update(1)
            responses.append(response)
        return responses

    # For multiple inputs, show overall progress
    with tqdm(
        total=len(inputs), desc="Overall progress", unit="input", position=0
    ) as overall_pbar:
        for i, input_source in enumerate(inputs):
            # Determine input type for better description
            input_type = "URL" if is_valid_url(input_source) else "File"
            input_name = (
                os.path.basename(input_source)
                if not is_valid_url(input_source)
                else input_source
            )

            # Handle different input types
            with tqdm(
                total=3,
                desc=f"Processing {input_type} ({i + 1}/{len(inputs)}): {input_name}",
                unit="step",
                position=1,
                leave=False,
            ) as pbar:
                # Step 1: Load content
                pbar.set_description(f"Loading content from {input_type}")
                if is_valid_url(input_source):
                    content = get_text_from_url(input_source)
                else:
                    content = read_input(input_source)
                pbar.update(1)

                # Step 2: Prepare prompt
                pbar.set_description("Preparing prompt")
                combined_prompt = f"{base_prompt} {content}".strip()
                pbar.update(1)

                # Step 3: Generate response with model
                pbar.set_description(f"Generating response with {model}")
                response = generate_response(combined_prompt, model)
                pbar.update(1)

                responses.append(response)

            # Update overall progress
            overall_pbar.update(1)

            # Add a small separator between input processing
            if i < len(inputs) - 1:
                print(f"✓ Completed {input_source}")

    return responses


def write_output(output_file, responses):
    """Write the responses to the output file and/or print to stdout."""
    try:
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                for response in responses:
                    f.write(response + "\n\n")
                    print(response + "\n")
        else:
            for response in responses:
                print(response + "\n")
    except Exception as e:
        logging.error("Failed to write output: %s", str(e))
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
        logging.warning("Unable to check app status: %s", str(e))
        return False


def main():
    """Main function."""
    try:
        base_prompt = args.prompt or DEFAULT_PROMPT
        responses = process_inputs(base_prompt, args.inputs, args.model)
        write_output(args.output, responses)
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", help="Base prompt", default=None)
    parser.add_argument(
        "-i", "--inputs", nargs="*", help="Paths to input files or URLs", default=[]
    )

    # Get available models dynamically
    available_models = get_available_models()

    parser.add_argument(
        "-m",
        "--model",
        choices=available_models,
        help="Model to use",
        default=DEFAULT_MODEL
        if DEFAULT_MODEL in available_models
        else available_models[0]
        if available_models
        else None,
    )
    parser.add_argument("-o", "--output", help="Output file", default=None)
    parser.add_argument("-t", "--temperature", help="Temperature", default=DEFAULT_TEMP)
    args = parser.parse_args()

    app_name = "Ollama"
    if not is_application_open(app_name):
        logging.warning("%s not running", app_name)
        if platform.system() == "Darwin":
            logging.info("Opening %s...", app_name)
            try:
                subprocess.run(["open", "-a", app_name], check=True)
                sleep(5)  # Giving it a little time to start
            except subprocess.CalledProcessError as e:
                logging.error("Failed to open %s: %s", app_name, str(e))
                sys.exit(1)
    main()
