#!/usr/bin/env python3
"""
A Python script to follow URL redirects and return the final address.
Optionally interacts with the system clipboard to read/write URLs.
"""

import sys
import logging
import argparse
import validators
import requests

try:
    import pyperclip as pc

    CLIPBOARD_ENABLED = True
except ImportError:
    CLIPBOARD_ENABLED = False
    logging.warning("::: Pyperclip module not found. Clipboard functionality disabled.")


def validate_url(url):
    """
    Validates the given URL.

    Args:
        url (str): The URL to validate.

    Raises:
        SystemExit: If the URL is invalid.
    """
    if not validators.url(url):
        logging.error(f"::: '{url}' is not a valid URL.")
        sys.exit(1)


def follow_redirect(input_url, timeout):
    """
    Follows the redirect of a given URL and returns the final URL.

    Args:
        input_url (str): The URL to follow.
        timeout (int): Timeout value in seconds for the request.

    Returns:
        str: The final URL after following redirects.

    Raises:
        SystemExit: If an error occurs during the request.
    """
    validate_url(input_url)
    try:
        response = requests.get(input_url, allow_redirects=True, timeout=timeout)
        if response.history:
            logging.info(response.history)
        return response.url
    except requests.RequestException as e:
        logging.error(f"::: Error during request: {e}")
        sys.exit(1)


def main(url, timeout):
    """
    Main function to execute the script logic.

    Args:
        url (str): The URL to process.
        timeout (int): Timeout value in seconds.

    Raises:
        SystemExit: If no valid URL is provided or an error occurs.
    """
    final_url = ""
    if url:
        final_url = follow_redirect(url, timeout)
    elif CLIPBOARD_ENABLED:
        clipboard_content = pc.paste()
        if validators.url(clipboard_content):
            final_url = follow_redirect(clipboard_content, timeout)
        else:
            logging.error("::: Clipboard does not contain a valid URL.")
            sys.exit(1)
    else:
        logging.error("::: No URL provided and clipboard functionality is disabled.")
        sys.exit(1)

    print(final_url)
    if CLIPBOARD_ENABLED:
        pc.copy(final_url)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    PARSER = argparse.ArgumentParser(
        description="Follows URL redirects and returns the final address"
    )
    PARSER.add_argument(
        "-u",
        "--url",
        help="Specify a URL manually. If not provided, the script will try to use the URL from the clipboard.",
        required=False,
    )
    PARSER.add_argument(
        "-t",
        "--timeout",
        help="Set a custom timeout value in seconds (default is 5 seconds).",
        type=int,
        default=5,
    )
    PARSER.add_argument(
        "--no-clipboard", action="store_true", help="Disable clipboard interaction."
    )
    ARGS = PARSER.parse_args()

    if ARGS.no_clipboard:
        CLIPBOARD_ENABLED = False

    if not ARGS.url and not CLIPBOARD_ENABLED:
        PARSER.print_help()
        sys.exit(1)

    main(ARGS.url, ARGS.timeout)
