#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Turns a twitter thread URL into a thethreaderapp.com URL for easier reading

import requests
import argparse
import sys

parser = argparse.ArgumentParser(description='Get the thread ID from a twitter URL')
parser.add_argument('url', help='the URL of the thread')
args = parser.parse_args()

url = args.url
valid_twitter_domains = ['twitter.com', 'mobile.twitter.com', 't.co']

def format_url(url):
    # remove www. from the URL
    if 'www.' in url:
        url = url.replace('www.', '')
    
    # add https:// if it's missing
    if not url.startswith('https://') and not url.startswith('http://'):
        url = 'https://' + url
    return url

url = format_url(url)

# Make a HEAD request to the URL to check if valid/still exists
check_url = lambda url: requests.head(url).status_code == 200

# get the thread ID from a twitter URL
def get_thread_id(url):
    if check_url(url):
        if not any(domain in url for domain in valid_twitter_domains):
            print('Invalid URL')
        else:
            # sanitize the URL of query strings
            url = url.split('?')[0]
            return url.split('/')[-1]
    else:
        print('Invalid URL')

thread_id = get_thread_id(url)

# Generating a "The Thread App" URL
def threader_app(thread_id):
    threader_domain = "https://threadreaderapp.com/thread/"
    threader_url = threader_domain + thread_id + ".html"
    print(threader_url)


if __name__ == '__main__':
    threader_app(thread_id)