#!/usr/bin/env python3

import requests

try: 
    import pyperclip as pc
except ImportError:
    print("::: Pyperclip module not found.")

def get_url(url):
    r = requests.get(url, allow_redirects=True)
    print(r.history)
    return r.url

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Follows URL redirects and returns a final address")
    parser.add_argument("URL", help="the URL to follow")
    args = parser.parse_args()
    url = args.URL

    # Copies the output to the system clipboard.
    output = get_url(url)
    print(output)
    pc.copy(output)