#!/usr/bin/env python3

# A simple dictionary and thesaurus script, using the Oxford Dictionary API

# Usage:
# thesaurus.py <word>

import os
import requests
import json
from dotenv import load_dotenv

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--endpoint', help='Get thesaurus results', default='entries', required=False)
parser.add_argument('word', help='The word you want to look up')
parser.usage = """
thesaurus.py [-h] [-e ENDPOINT] word

The endpoint can be one of the following:
    - entries
    - thesaurus
"""

args = parser.parse_args()

if os.path.isfile('.env'):
    load_dotenv('.env')

app_id = os.getenv('APP_ID')
app_key = os.getenv('APP_KEY')
language = 'en-us'
base_url = "https://od-api.oxforddictionaries.com/api/v2"


def get_word(endpoint, word):
    url = f"{base_url}/{endpoint}/{language}/{word}"
    r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})
    results = json.dumps(r.json())
    return results


def main():
    endpoint = args.endpoint
    word = args.word.lower()
    results = get_word(endpoint, word)
    print(results)


if __name__ == '__main__':
    main()
