#!/usr/bin/env python3

import requests
import urllib.parse
import argparse
import json
import os

# Options and arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', help='URL to summarize', required=True)
parser.add_argument('-k', '--key', help='API key', required=False)
args = parser.parse_args()

if os.path.isfile('.env'): # Checking if .env file exists
    from dotenv import load_dotenv
    load_dotenv() # importing .env file as a environment variable(s)
    API_key = os.environ['SMMRY_API_KEY']
else:
    API_key = args.key

article_URL_raw = args.url
article_URL_formatted = urllib.parse.quote_plus(article_URL_raw)
url = "https://api.smmry.com?SM_API_KEY=" + API_key + "&SM_LENGTH=10&SM_URL=" + article_URL_formatted

payload = {}
headers= {}

response = requests.request("POST", url, headers=headers, data = payload)

if __name__ == '__main__':
    if not API_key:
        print("Please provide an API key")
        exit(1)
    else:
        #print(response.text.encode('utf8'))
        json_data = json.loads(response.text.encode('utf8'))
        print(json_data['sm_api_content'])