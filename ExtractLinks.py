#!/usr/bin/env python3

#simple script to extract links from a web page.

import sys
import requests
from bs4 import BeautifulSoup


url = sys.argv[1] #the url of the page we're extracting links from.
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')

urls = []
for link in soup.find_all('a'):
	print(link.get('href'))

