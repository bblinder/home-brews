#!/usr/bin/env python3

"""
A simple dictionary and thesaurus script, using the Oxford Dictionary API
"""

import argparse
import json
import os

import requests
from dotenv import load_dotenv

parser = argparse.ArgumentParser()
parser.add_argument(
    "-e", "--endpoint", help="Get thesaurus results", default="entries", required=False
)
parser.add_argument("word", help="The word you want to look up")
parser.usage = """
thesaurus.py [-h] [-e ENDPOINT] word

The endpoint can be one of the following:
    - entries
    - thesaurus
"""

args = parser.parse_args()

if os.path.isfile(".env"):
    load_dotenv(".env")

app_id = os.getenv("APP_ID")
app_key = os.getenv("APP_KEY")
LANGUAGE = "en-us"
BASE_URL = "https://od-api.oxforddictionaries.com/api/v2"


def get_word(endpoint, word):
    url = f"{BASE_URL}/{endpoint}/{LANGUAGE}/{word}"
    r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})
    results = json.dumps(r.json())
    return results


def main():
    endpoint = args.endpoint
    word = args.word.lower()
    results = get_word(endpoint, word)
    print(json.dumps(json.loads(results), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
