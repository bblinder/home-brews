#!/usr/bin/env python3

"""
Sales As Code: randomly selects a sales-y buzzword from a google sheet.
"""

import argparse
import logging
import os
import random
import sys

import gspread
from cachetools import TTLCache
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO)

cache = TTLCache(maxsize=1, ttl=3600)


def authenticate():
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


def fetch_sales_terms(gsheet):
    """Fetch sales terms from Google Sheets."""
    try:
        sales_terms = gsheet.col_values(1)[1:]
        return sales_terms
    except Exception as err:
        logging.error("Failed to fetch sales terms: %s", err)
        return None


def cache_sales_terms(sales_terms):
    """Cache sales terms locally."""
    try:
        cache["sales_terms"] = sales_terms
    except Exception as err:
        logging.error("Failed to cache sales terms: %s", err)


def get_sales_terms():
    """Get sales terms from Google Sheets, cache them locally, and pick one at random."""
    cached_terms = cache.get("sales_terms")
    if cached_terms:
        sales_terms = cached_terms
    else:
        gsheet = authenticate()
        if not gsheet:
            logging.error("Failed to authenticate with Google Sheets. Exiting...")
            return None
        sales_terms = fetch_sales_terms(gsheet)
        if not sales_terms:
            return None
        cache_sales_terms(sales_terms)
    return random.choice(sales_terms)


def spongecase(term):
    """SpOngECAse tHe oUtPUt."""
    return "".join(
        char.upper() if random.randint(0, 1) else char.lower() for char in term
    )


def ask_if_rep_talking():
    """A while loop asking if the rep is still talking."""
    while True:
        try:
            answer = input("Is the rep still talking? (y/n) ").lower()
            if answer != "y":
                break
            sales_term = get_sales_terms()
            if args.spongecase:
                print(spongecase(sales_term))
            else:
                print(f"{sales_term}")
        except Exception as err:
            logging.error("Failed to get sales term: %s", err)


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
    argparser.add_argument(
        "--cachebust",
        required=False,
        action="store_true",
        help="Bust the cache",
    )
    args = argparser.parse_args()

    if not authenticate():
        logging.error("Failed to authenticate with Google Sheets. Exiting...")
        sys.exit(1)

    ask_if_rep_talking()
