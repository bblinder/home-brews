#!/usr/bin/env python3

"""
Derived from Justine Tunney's and Mozilla's llamafile project. See: https://justine.lol/oneliners/
This script is used to summarize the text from a given URL or text file
using the mistral-7b llamafile: https://github.com/Mozilla-Ocho/llamafile


TODO:
- [ ] Add support for multiple URLs
- [x] Add support for text files
- [ ] Add support for chunking based on token count
"""

import sys
import os
import argparse
import re
import random
import shlex
import subprocess
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
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
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
        proxy_url = f"https://1ft.io/{url}"
        text = fetch_url(proxy_url)

    return text


def summarize_text(
    text, llamafile_path, summarization_prompt=DEFAULT_SUMMARIZATION_PROMPT
):
    """Summarize the text using llamafile."""
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


def fallback_summarize_text(
    url, llamafile_path, summarization_prompt=DEFAULT_SUMMARIZATION_PROMPT
):
    """Fallback method to summarize text using the original Bash script logic."""
    cmd = (
        f"echo '{summarization_prompt}' | "
        f"links -codepage utf-8 -force-html -width 500 -dump '{url}' | "
        f"sed 's/   */ /' | "
        f"{llamafile_path} -c {CHAR_COUNT} -f /dev/stdin --temp {TEMPERATURE} -n {NUM_TOKENS} --silent-prompt"
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


def read_text_from_file(file_path):
    """Read and return text from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


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
                text = read_text_from_file(input_str)
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
                summaries.append(f"Input: {input_str}\nSummary:\n{summary}\n")
            else:
                bar.text("-> Failed to retrieve summary.")

    combined_summaries = "\n".join(summaries)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(combined_summaries)
        print(f"Summaries saved to {args.output}")
    else:
        print(combined_summaries)


if __name__ == "__main__":
    main()
