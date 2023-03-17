#!/usr/bin/env python3

"""
Sales As Code: randomly selects a sales-y buzzword from a google sheet.
"""

import argparse
import logging
import os
import random
import sys
import time

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO)


def authenticate(args):
    """Authenticate with Google Sheets API and return the gsheet object."""
    if args.credentials:
        creds = args.credentials
    else:
        load_dotenv()
        creds = os.getenv("SALES_AS_CODE_CREDS")

    if not creds:
        logging.error("No credentials found. Exiting...")
        sys.exit(1)

    credential = ServiceAccountCredentials.from_json_keyfile_name(
        creds,
        [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )

    client = gspread.authorize(credential)
    gsheet = client.open("Sales As Code").sheet1

    return gsheet


def get_sales_terms(args):
    """Get sales terms from Google Sheets, cache them locally, and pick one at random."""
    gsheet = authenticate(args)
    temp_directory = os.path.join(os.path.expanduser("~"), ".cache", "salesascode")
    temp_file = os.path.join(temp_directory, "sales_terms.txt")

    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)

    try:
        if os.path.exists(temp_file):
            # check the timestamp of the file
            file_timestamp = os.path.getmtime(temp_file)
            current_timestamp = time.time()
            if current_timestamp - file_timestamp > 3600:
                # the file is older than 1 hour, re-fetch the sales terms
                sales_terms = gsheet.col_values(1)[1:]
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(sales_terms))
            else:
                # the file is younger than 1 hour, use the cached sales terms
                with open(temp_file, "r", encoding="utf-8") as f:
                    sales_terms = f.read().splitlines()
        else:
            # the file doesn't exist, fetch the sales terms and cache them
            sales_terms = gsheet.col_values(1)[1:]
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("\n".join(sales_terms))

        return random.choice(sales_terms)
    except Exception as e:
        logging.error(e)
        sys.exit(1)


def spongecase(term):
    """SpOngECAse tHe oUtPUt."""
    return "".join(
        char.upper() if random.randint(0, 1) else char.lower() for char in term
    )


def ask_if_rep_talking(args):
    """A while loop asking if the rep is still talking."""
    while True:
        try:
            answer = input("Is the rep still talking? (y/n) ").lower()
            if answer != "y":
                break
            sales_term = get_sales_terms(args)
            if args.spongecase:
                print(spongecase(sales_term))
            else:
                print(f"{sales_term}")
        except Exception as e:
            logging.error(e)
            sys.exit(1)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-s",
        "--spongecase",
        required=False,
        action="store_true",
        help="SpONgECasE ThE oUtPut",
    )
    argparser.add_argument(
        "-c",
        "--credentials",
        required=False,
        help="Path to credentials file",
    )
    args = argparser.parse_args()

    ask_if_rep_talking(args)
