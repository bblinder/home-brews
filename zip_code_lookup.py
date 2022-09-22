#!/usr/bin/env python3

# Queries a list of zip codes (CSV) against the SmartyStreets API

import argparse
import csv
import sys

import yaml

argparser = argparse.ArgumentParser(description="Query SmartyStreets API")
argparser.add_argument("file_name", help="CSV file with zip codes")
args = argparser.parse_args()

with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
    auth_id = config["auth_id"]
    auth_token = config["auth_token"]

file_name = args.file_name

try:
    import requests  # Finally!
except ImportError:
    print("Can't import Requests -- check that it's installed!")
    print("Exiting...")
    sys.exit(1)


def zip_request():
    with open(file_name, "U") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            value_from_csv = row[0]
            # headers = {"content-type": "application/json"}
            url = f"https://us-zipcode.api.smartystreets.com/lookup?auth-id={auth_id}&auth-token={auth_token}&zipcode={value_from_csv}"
            r = requests.get(url, timeout=10)
            print(r.json())


# Now doing the actual work...
if __name__ == "__main__":
    zip_request()
