#!/usr/bin/env python3

#simple script to extract links from a web page.

import sys
import requests
import argparse
#from gooey import Gooey, GooeyParser
from bs4 import BeautifulSoup

#@Gooey
def extract_links():
	#parser = GooeyParser(description="List the URLs on a page")
	#parser.add_argument('url', help="The URL of the page we're extracting links from", type=str)
	parser = argparse.ArgumentParser(description='List the URLs on a page')
	parser.add_argument('url', help="The URL of the page we're extracting links from", type=str)
	args = vars(parser.parse_args())
	#print(args)

	#url = input("URL of the page: ")
	url = sys.argv[1] #the url of the page we're extracting links from.
	reqs = requests.get(url)
	soup = BeautifulSoup(reqs.text, 'html.parser')

	urls = []
	for link in soup.find_all('a'):
		print(link.get('href'))

extract_links()