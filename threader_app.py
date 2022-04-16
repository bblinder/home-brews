#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Turns a twitter thread URL into a thethreaderapp.com URL for easier reading

import requests
import argparse
import sys

parser = argparse.ArgumentParser(description='Get the thread ID from a twitter URL')
parser.add_argument('url', help='the URL of the thread')
args = parser.parse_args()

valid_twitter_domains = ['twitter.com', 'mobile.twitter.com', 't.co']


def format_url():
    twitter_url = args.url
    # remove www. from the URL
    if 'www.' in twitter_url:
        twitter_url = twitter_url.replace('www.', '')

    # add https:// if it's missing
    if not twitter_url.startswith('https://') and not twitter_url.startswith('http://'):
        twitter_url = 'https://' + twitter_url
    return twitter_url


url = format_url()


# Make a HEAD request to the URL to check if valid/still exists
def check_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


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
        sys.exit(1)


# Generating a "The Thread App" URL
def threader_app():
    thread_id = get_thread_id(url)
    threader_domain = "https://threadreaderapp.com/thread/"
    threader_url = threader_domain + thread_id + ".html"
    print(threader_url)


if __name__ == '__main__':
    threader_app()
