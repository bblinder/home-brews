#!/usr/bin/env python3

"""
Derived from Justine Tunney's and Mozilla's llamafile project. See: https://justine.lol/oneliners/
This script is used to summarize the text from a given URL 
using the mistral-7b llamafile and the 'links' browser.
https://github.com/Mozilla-Ocho/llamafile
"""

import argparse
import re
import shlex
import subprocess
from urllib.parse import quote
from alive_progress import alive_bar
import requests
from bs4 import BeautifulSoup

TIMEOUT_SECONDS = 5  # Global constant for timeout


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
    """Scrape and process text from URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    try:
        response = requests.get(
            url, allow_redirects=True, timeout=TIMEOUT_SECONDS, headers=headers
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text()
            text = re.sub(r"[\s\xa0]+", " ", text).strip()
            return text
        else:
            return None
    except requests.RequestException:
        return None


def summarize_text(text, llamafile_path):
    """Summarize the text using llamafile."""
    escaped_text = shlex.quote(f"[INST]Summarize the following text: {text} [/INST]")
    cmd = f"echo {escaped_text} | {llamafile_path} -c 6700 -f /dev/stdin --temp 0 -n 500 --silent-prompt"
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


def fallback_summarize_text(url, llamafile_path):
    """Fallback method to summarize text using the original Bash script logic."""
    cmd = (
        f"echo '[INST]Summarize the following text:' | "
        f"links -codepage utf-8 -force-html -width 500 -dump '{url}' | "
        f"sed 's/   */ /' | "
        f"{llamafile_path} -c 6700 -f /dev/stdin --temp 0 -n 500 --silent-prompt"
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


def main():
    """Main function to parse arguments and summarize text from URLs."""
    parser = argparse.ArgumentParser(description="Summarize text from multiple URLs.")
    parser.add_argument("urls", nargs="+", help="The URLs to summarize text from.")
    parser.add_argument("llamafile_path", help="The path to the llamafile executable.")
    parser.add_argument(
        "-o",
        "--output",
        help="Optional output file to save the summaries.",
        default=None,
    )
    args = parser.parse_args()

    summaries = []

    for url in args.urls:
        with alive_bar(3, bar="bubbles", spinner="dots") as bar:
            bar.text("-> Attempting to scrape text from URL...")
            text = get_text_from_url(url)
            bar()  # Increment the progress bar

            if text:
                bar.text("-> Summarizing text...")
                summary = summarize_text(text, args.llamafile_path)
                bar()  # Increment the progress bar after summarizing
            else:
                bar.text("-> Falling back to Bash logic for summarizing...")
                summary = fallback_summarize_text(url, args.llamafile_path)
                bar()  # Increment the progress bar after fallback

            if summary.strip():
                bar.text("-> Done!")
                summaries.append(f"URL: {url}\nSummary:\n{summary}\n")
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
