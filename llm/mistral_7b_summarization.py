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
Derived from Justine Tunney's and Mozilla's llamafile project.
This script is used to summarize the text from a given URL or file
using the mistral-7b llamafile.
"""

import argparse
import os
import random
import re
import subprocess
import sys
from urllib.parse import urlparse

import requests
from alive_progress import alive_bar
from bs4 import BeautifulSoup

TIMEOUT_SECONDS = 5
DEFAULT_SUMMARIZATION_PROMPT = "[INST]Summarize the following text:"

CHAR_COUNT = 6700
TEMPERATURE = 0
NUM_TOKENS = 500

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
]


def get_user_agent():
    return random.choice(USER_AGENTS)


def is_valid_url_format(url):
    """Check if the string is formatted as a valid HTTP/HTTPS URL."""
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except ValueError:
        return False


def get_text_from_url(url):
    """Scrape and process text from URL."""
    headers = {"User-Agent": get_user_agent()}

    try:
        response = requests.get(
            url, allow_redirects=True, timeout=TIMEOUT_SECONDS, headers=headers
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        return re.sub(r"[\s\xa0]+", " ", text).strip()
    except requests.RequestException as e:
        print(f"\nFailed to fetch URL {url}: {e}")
        return None


def summarize_text(
    text, llamafile_path, summarization_prompt=DEFAULT_SUMMARIZATION_PROMPT
):
    """Summarize the text using llamafile securely using subprocess pipes."""
    prompt = f"{summarization_prompt} {text} [/INST]"
    cmd = [
        "sh",  # Explicitly invoke the shell to read the APE polyglot header
        llamafile_path,
        "-c",
        str(CHAR_COUNT),
        "-ngl",
        "9999",
        "-f",
        "/dev/stdin",
        "--temp",
        str(TEMPERATURE),
        "-n",
        str(NUM_TOKENS),
        "--silent-prompt",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        output = re.sub(r"</s>$", "", result.stdout)
        return output.strip()
    except subprocess.CalledProcessError as e:
        print(f"\nError in llamafile execution: {e.stderr}")
        return ""


def read_input(input_path):
    """Read the content of the input file, with support for PDFs."""
    try:
        file_extension = os.path.splitext(input_path)[1].lower()
        if file_extension == ".pdf":
            import fitz  # PyMuPDF

            doc = fitz.open(input_path)
            return "".join([page.get_text() for page in doc])

        with open(input_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"\nFailed to read input from {input_path}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Summarize text from URLs or files using Mistral llamafile."
    )
    parser.add_argument(
        "inputs", nargs="*", help="The URLs or file paths to summarize from."
    )
    parser.add_argument(
        "-lf",
        "--llamafile_path",
        required=True,
        help="The path to the llamafile executable.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional output file to save the summaries.",
        default=None,
    )
    args = parser.parse_args()

    # Validate llamafile exists and is executable
    if not os.path.isfile(args.llamafile_path) or not os.access(
        args.llamafile_path, os.X_OK
    ):
        sys.exit(
            f"Error: Llamafile at '{args.llamafile_path}' does not exist or is not executable."
        )

    input_sources = args.inputs if args.inputs else [sys.stdin.read().strip()]
    summaries = []

    for input_str in input_sources:
        if not input_str:
            continue

        with alive_bar(
            3, bar="bubbles", spinner="dots", title=f"Processing {input_str[:20]}..."
        ) as bar:
            # Step 1: Resolve Text
            bar.text("Reading source...")
            if os.path.isfile(input_str):
                text = read_input(input_str)
            elif is_valid_url_format(input_str):
                text = get_text_from_url(input_str)
            else:
                text = input_str
            bar()

            # Step 2 & 3: Summarize if text exists
            if text:
                bar.text("Summarizing text...")
                summary = summarize_text(text, args.llamafile_path)
                bar()

                bar.text("Finalizing...")
                if summary:
                    summaries.append(f"Input: {input_str}\n--------\n{summary}\n")
                bar()
            else:
                bar.text("Failed to retrieve text.")
                bar()
                bar()  # Finish the bar to avoid UI hanging

    combined_summaries = "\n".join(summaries)

    if combined_summaries:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as file:
                file.write(combined_summaries)
            print(f"Summaries saved to {args.output}")
        else:
            print("\n" + combined_summaries)
    else:
        print("No summaries were generated.")


if __name__ == "__main__":
    main()
