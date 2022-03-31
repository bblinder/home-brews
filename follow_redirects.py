#!/usr/bin/env python3

import requests

try: 
    import pyperclip as pc
except ImportError:
    print("::: Pyperclip module not found.")
    exit(1)

# Follow URL redirect, print any hops along the way
def follow_redirect():
    # By default, whatever's currently in the clipboard gets pasted.
    input = pc.paste()
    r = requests.get(input, allow_redirects=True)
    
    if r.history:
        print(r.history)
    return r.url

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Follows URL redirects and returns a final address")
    parser.add_argument(
        "-u", "--url", 
        help="the URL to follow. By default, whatever's currently in the clipboard gets pasted. Use '-u' to specify a URL manually.",
        required=False)
    args = parser.parse_args()
    url = args.url

    # Copies the output to the system clipboard.
    output = follow_redirect()
    print(output)
    pc.copy(output)