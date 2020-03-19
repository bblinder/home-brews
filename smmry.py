#!/usr/bin/env python3

import requests
import sys
import urllib.parse

API_key = '[API Key]'
article_URL_raw = sys.argv[1]
article_URL_formatted = urllib.parse.quote_plus(news_article)
url = "https://api.smmry.com?SM_API_KEY=" + API_key + "&SM_LENGTH=10&SM_URL=" + news_article_formatted

payload = {}
headers= {}

response = requests.request("POST", url, headers=headers, data = payload)

#json_data = json.loads(response.text.encode('utf8'))
print(response.text.encode('utf8'))

