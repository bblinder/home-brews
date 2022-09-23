#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib.parse

import requests

# Options and arguments
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="URL to summarize", required=True)
parser.add_argument("-k", "--key", help="API key", required=False)
args = parser.parse_args()

if args.key:
    API_key = args.key
elif os.path.isfile(".env"):
    from dotenv import load_dotenv

    load_dotenv()
    API_key = os.getenv("SMMRY_API_KEY")

article_URL_raw = args.url
article_URL_formatted = urllib.parse.quote_plus(article_URL_raw)
url = f"https://api.smmry.com?SM_API_KEY={API_key}&SM_LENGTH=10&SM_URL={article_URL_formatted}"

payload = {}
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, timeout=10)

if __name__ == "__main__":
    if not API_key:
        print("Please provide an API key")
        sys.exit(1)
    else:
        # print(response.text.encode('utf8'))
        json_data = json.loads(response.text.encode("utf8"))
        print(json_data["sm_api_content"])
