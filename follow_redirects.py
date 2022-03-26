#!/usr/bin/env python3

import requests

try: 
    import pyperclip as pc
except ImportError:
    print("::: Pyperclip module not found.")
    exit(1)

# Follow redirect of url
def follow_redirect(url):
    r = requests.get(url, allow_redirects=True)
    if r.history:
        print(r.history)
    return r.url

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Follows URL redirects and returns a final address")
    parser.add_argument("URL", help="the URL to follow")
    args = parser.parse_args()
    url = args.URL

    # Copies the output to the system clipboard.
    output = follow_redirect(url)
    print(output)
    pc.copy(output)