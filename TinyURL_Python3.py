#!/usr/bin/env python3

"""Use the tinyURL API to shorten URLs."""

import contextlib
import requests
from urllib.parse import urlencode
import argparse
import sys

argparser = argparse.ArgumentParser(description='Shorten URLs with the TinyURL API.')
argparser.add_argument('urls', metavar='URL', nargs='+', help='URLs to shorten')
args = argparser.parse_args()

def make_tiny(url):
    """Return a tiny version of the given URL."""
    request_url = 'http://tinyurl.com/api-create.php?' + urlencode({'url':url})
    with contextlib.closing(requests.get(request_url)) as response:
        return response.text

def main():
    """Run the main program."""
    for tinyurl in map(make_tiny, sys.argv[1:]):
        print(tinyurl)

if __name__ == '__main__':
    main()
    exit(0)