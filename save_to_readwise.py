#!/usr/bin/env python3

"""
Adds an article to Readwise Reader.
"""

import os
import argparse
import requests

# Readwise Auth Token
READWISE_TOKEN = os.environ.get("READWISE_TOKEN")
API_ENDPOINT = "https://readwise.io/api/v3/save/"

args = argparse.ArgumentParser()
args.add_argument("URL", help="URL of the article")
args.add_argument("--tags", nargs="*", help="Tags to add to the article")
args = args.parse_args()


def add_article(url, tags):
    """Add an article to Readwise.

    Args:
        url (str): URL of the article.
        tags (list): List of tags to add to the article.
    """
    response = requests.post(
        url=API_ENDPOINT,
        headers={
            "Authorization": f"Token {READWISE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"url": url, "tags": tags},
    )

    if response.status_code in {200, 201}:
        print(f"Added {url} to Readwise.")
    else:
        print(f"Failed to add {url}. Status code: {response.status_code}")


def main():
    """Constructing the request and adding tags"""
    add_article(args.URL, args.tags)


if __name__ == "__main__":
    main()
