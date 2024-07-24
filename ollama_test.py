#!/usr/bin/env python3

"""
Using the Ollama python lib to chat with supported models.

TODO:
- [x] Add URL summarization
- [x] Replace print statements with logging
- [ ] Handle multiple inputs in the command line
"""

import sys
import os
import subprocess


def bootstrap_venv():
    """Bootstraps a python virtual environment (venv) for the script to run in."""
    SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
    VENV_DIR = os.path.join(SCRIPT_DIR, "venv")
    IS_WINDOWS = sys.platform.startswith("win")
    VENV_BIN_DIR = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin")
    VENV_ACTIVATE_BASH = os.path.join(VENV_BIN_DIR, "activate")
    REQUIREMENTS_PATH = os.path.join(SCRIPT_DIR, "requirements.txt")
    PYTHON_EXECUTABLE = os.path.join(
        VENV_BIN_DIR, "python3.exe" if IS_WINDOWS else "python3"
    )

    if not os.path.exists(VENV_DIR):  # No venv found, creating one
        print("No virtual environment found. Setting one up...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        print(f"Virtual environment created at {VENV_DIR}")

    if (
        "VIRTUAL_ENV" not in os.environ
    ):  # Venv is not active, activate and re-run the script
        if IS_WINDOWS:
            command = (
                f'"{VENV_ACTIVATE_BASH}" && "{PYTHON_EXECUTABLE}" "{__file__}" '
                + " ".join(sys.argv[1:])
            )
            subprocess.check_call(command, shell=True)
        else:
            command = f"source \"{VENV_ACTIVATE_BASH}\" && \"{PYTHON_EXECUTABLE}\" \"{__file__}\" {' '.join(map(lambda x: '\"' + x + '\"', sys.argv[1:]))}"
            os.execle("/bin/bash", "bash", "-c", command, os.environ)
        sys.exit()
    else:  # Venv is active, ensure dependencies are installed
        if os.path.exists(REQUIREMENTS_PATH):
            print("Installing dependencies from requirements.txt...")
            subprocess.check_call(
                [
                    PYTHON_EXECUTABLE,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    REQUIREMENTS_PATH,
                    "--upgrade",
                ],
                cwd=SCRIPT_DIR,
            )
        else:
            print("requirements.txt not found, skipping dependency installation.")


if sys.version_info >= (3, 12):
    bootstrap_venv()
    os.system("cls" if os.name == "nt" else "clear")  # Clear the terminal screen

import platform
import pathlib
import argparse
import logging
import random
import re
from time import sleep
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
import ollama
from tqdm import tqdm

SUPPORTED_MODELS = ["mistral", "llama3.1"]
DEFAULT_TEMP = 0.0
TIMEOUT_SECONDS = 5
DEFAULT_PROMPT = "As a helpful assistant, your task is to provide a concise and precise summary of the given document. Focus on extracting the main points and relevant details from the text while maintaining brevity in your response. Ensure that your summary captures the essence of the conversation or discussion without sacrificing accuracy. Please note that you should be able to handle various types of documents, such as interviews, meetings, transcripts, or presentations. Your response should be flexible enough to allow for different topics and contexts while still providing a clear and focused summary."

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
    """Scrape and process text from URL. Use proxy if access is forbidden."""
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
        response = ollama.chat(
            model=model,
            options={"temperature": DEFAULT_TEMP},
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
    except Exception as e:
        logging.error("Failed to generate response: %s", str(e))
        sys.exit(1)


def process_inputs(base_prompt, inputs, model):
    """Combine base prompt with content from inputs to generate responses."""
    responses = []
    if inputs:
        for input_source in tqdm(inputs, desc="Processing inputs"):
            if is_valid_url(input_source):
                content = get_text_from_url(input_source)
            else:
                content = read_input(input_source)
            combined_prompt = f"{base_prompt} {content}".strip()
            response = generate_response(combined_prompt, model)
            responses.append(response)
    else:
        response = generate_response(base_prompt, model)
        responses.append(response)
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
    args = argparse.ArgumentParser()
    args.add_argument("-p", "--prompt", help="Base prompt", default=None)
    args.add_argument(
        "-i", "--inputs", nargs="*", help="Paths to input files or URLs", default=[]
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
