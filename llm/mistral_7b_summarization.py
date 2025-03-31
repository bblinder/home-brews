#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "alive-progress",
#     "beautifulsoup4",
#     "pymupdf",
#     "requests",
# ]
# ///

"""
Derived from Justine Tunney's and Mozilla's llamafile project. See: https://justine.lol/oneliners/
This script is used to summarize the text from a given URL or file
using the mistral-7b llamafile: https://github.com/Mozilla-Ocho/llamafile

TODO:
- [x] Add support for multiple URLs
- [x] Add support for reading multiple URLs from a text file
- [x] Add support for text files
- [ ] Add support for chunking based on token count
"""

import sys
import os
import subprocess


# def bootstrap_venv():
#     """Bootstraps a python virtual environment (venv) for the script to run in."""
#     SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
#     VENV_DIR = os.path.join(SCRIPT_DIR, "venv")
#     IS_WINDOWS = sys.platform.startswith("win")
#     VENV_BIN_DIR = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin")
#     VENV_ACTIVATE_BASH = os.path.join(VENV_BIN_DIR, "activate")
#     REQUIREMENTS_PATH = os.path.join(SCRIPT_DIR, "requirements.txt")
#     PYTHON_EXECUTABLE = os.path.join(
#         VENV_BIN_DIR, "python3.exe" if IS_WINDOWS else "python3"
#     )

#     if not os.path.exists(VENV_DIR):  # No venv found, creating one
#         print("No virtual environment found. Setting one up...")
#         subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
#         print(f"Virtual environment created at {VENV_DIR}")

#     if (
#         "VIRTUAL_ENV" not in os.environ
#     ):  # Venv is not active, activate and re-run the script
#         if IS_WINDOWS:
#             command = (
#                 f'"{VENV_ACTIVATE_BASH}" && "{PYTHON_EXECUTABLE}" "{__file__}" '
#                 + " ".join(sys.argv[1:])
#             )
#             subprocess.check_call(command, shell=True)
#         else:
#             command = f"source \"{VENV_ACTIVATE_BASH}\" && \"{PYTHON_EXECUTABLE}\" \"{__file__}\" {' '.join(map(lambda x: '\"' + x + '\"', sys.argv[1:]))}"
#             os.execle("/bin/bash", "bash", "-c", command, os.environ)
#         sys.exit()
#     else:  # Venv is active, ensure dependencies are installed
#         if os.path.exists(REQUIREMENTS_PATH):
#             print("Installing dependencies from requirements.txt...")
#             subprocess.check_call(
#                 [
#                     PYTHON_EXECUTABLE,
#                     "-m",
#                     "pip",
#                     "install",
#                     "-r",
#                     REQUIREMENTS_PATH,
#                     "--upgrade",
#                 ],
#                 cwd=SCRIPT_DIR,
#             )
#         else:
#             print("requirements.txt not found, skipping dependency installation.")


if sys.version_info >= (3, 12):
    #bootstrap_venv()
    os.system("cls" if os.name == "nt" else "clear")  # Clear the terminal screen

import argparse
import re
import random
import shlex
from urllib.parse import quote
from alive_progress import alive_bar
import requests
from bs4 import BeautifulSoup

TIMEOUT_SECONDS = 5  # Global constant for timeout
DEFAULT_SUMMARIZATION_PROMPT = "[INST]Summarize the following text:"

# Default arguments for llamafile. DO NOT CHANGE these unless you know what you're doing.
CHAR_COUNT = 6700  # We don't want to exceed Mistral's 7,000 token context size.
TEMPERATURE = 0  # keeping it nice and deterministic.
NUM_TOKENS = 500

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
]


def get_user_agent():
    """Get a random user agent from the list."""
    return random.choice(USER_AGENTS)


def is_valid_url(url):
    """Check if the URL is valid and follow redirects."""
    try:
        encoded_url = quote(url, safe=":/")
        response = requests.get(
            encoded_url, allow_redirects=True, timeout=TIMEOUT_SECONDS
        )
        print(
            f"Encoded URL: {encoded_url}, Status Code: {response.status_code}"
        )  # Debugging print
        return response.status_code < 400
    except requests.RequestException as e:
        print(f"URL validation error: {e}")
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

    # If direct access is forbidden (403), try using the proxy
    if text is None:
        print("Trying to access URL via proxy...")
        proxy_url = f"https://1ft.io/{url}"
        print(f"Proxy URL: {proxy_url}")  # Debugging print
        text = fetch_url(proxy_url)

    return text


def summarize_text(
    text, llamafile_path, summarization_prompt=DEFAULT_SUMMARIZATION_PROMPT
):
    """Summarize the text using llamafile and trim output to content after [/INST]."""
    escaped_text = shlex.quote(f"{summarization_prompt} {text} [/INST]")
    cmd = f"echo {escaped_text} | {llamafile_path} -c {CHAR_COUNT} -ngl 9999 -f /dev/stdin --temp {TEMPERATURE} -n {NUM_TOKENS} --silent-prompt"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        output = result.stdout
        # Extract content after [/INST]
        #output_after_inst = output.split("[/INST]", 1)[1] if "[/INST]" in output else ""
        #return output_after_inst.strip()
        output = re.sub(r'</s>$', '', output) # Remove </s> tag at the end of the output
        return output.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error in llamafile execution: {e}")
        return ""


def fallback_summarize_text(
    url, llamafile_path, summarization_prompt=DEFAULT_SUMMARIZATION_PROMPT
):
    """Fallback method to summarize text using the original Bash script logic."""
    cmd = (
        f"echo '{summarization_prompt}' | "
        f"links -codepage utf-8 -force-html -width 500 -dump '{url}' | "
        f"sed 's/   */ /' | "
        f"{llamafile_path} -c {CHAR_COUNT} -ngl 9999 -f /dev/stdin --temp {TEMPERATURE} -n {NUM_TOKENS} --silent-prompt"
    )
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        print(f"Error occurred while processing URL: {url}")
        return ""


def read_input(input_path):
    """Read the content of the input file, with support for PDFs."""
    try:
        file_extension = os.path.splitext(input_path)[1].lower()
        if file_extension == ".pdf":
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(input_path)
                text = "".join([page.get_text() for page in doc])
                return text
            except ImportError as e:
                raise SystemExit(
                    "Error: PyMuPDF (fitz) is required to read PDF files. Install it via pip."
                ) from e
        elif os.path.exists(input_path):
            with open(input_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise FileNotFoundError(f"Error: File {input_path} does not exist.")
    except Exception as e:
        print(f"Failed to read input from {input_path}: {e}")
        sys.exit(1)


def is_file_path(input_str):
    """Check if the input string is a valid file path."""
    return os.path.isfile(input_str)


def main():
    """Main function to parse arguments and summarize text from URLs or text files."""
    parser = argparse.ArgumentParser(description="Summarize text from multiple URLs.")
    parser.add_argument(
        "inputs", nargs="*", help="The URLs or file paths to summarize from."
    )
    parser.add_argument(
        "-lf", "--llamafile_path", help="The path to the llamafile executable."
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional output file to save the summaries.",
        default=None,
    )
    args = parser.parse_args()

    summaries = []
    input_sources = args.inputs

    # Check if inputs are provided, if not, read from stdin
    if not input_sources:
        input_text = sys.stdin.read().strip()
        input_sources = [input_text]

    for input_str in input_sources:
        with alive_bar(3, bar="bubbles", spinner="dots") as bar:
            bar.text("-> Processing input...")

            if is_file_path(input_str):
                text = read_input(input_str)
            elif is_valid_url(input_str):
                text = get_text_from_url(input_str)
            else:
                text = input_str  # Directly use the input string as text

            bar()  # Increment the progress bar

            if text:
                bar.text("-> Summarizing text...")
                summary = summarize_text(text, args.llamafile_path)
                bar()
            else:
                bar.text("-> Failed to retrieve text.")
                continue

            if summary.strip():
                bar.text("-> Done!")
                summaries.append(f"Input: {input_str}\n--------\n{summary}\n")
            else:
                bar.text("-> Failed to retrieve summary.")

    combined_summaries = "\n".join(summaries)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(combined_summaries)
        print(combined_summaries)
        print(f"Summaries saved to {args.output}")
    else:
        print(combined_summaries)


if __name__ == "__main__":
    main()
