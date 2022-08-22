#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# A tool to follow redirects

# Take URL as input and send it to the server
# Follow redirects and print them out
# Copy final URL to clipboard

import requests
from flask import Flask, request, url_for

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def process_request():
    # process the request as query string
    # follow redirects and print them out
    #url = request.args.get('url').encode('utf-8')
    url = request.args.get('url')

    # add http if it's not there
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    print(f"URL is: {url}")


    r = requests.get(url, allow_redirects=True)
    if r.history:
        return url_for(r.history)
        #return f"<h1>{r.history}</h1>"
    else:
        return f"<h1>{r.url}</h1>"

app.run(debug=True)