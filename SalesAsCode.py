#!/usr/bin/env python3

"""
Sales As Code: randomly selects a sales-y buzzword from a google sheet.
"""

import os
import random
import sys

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

CREDS = os.getenv("SALES_AS_CODE_CREDS")

if not CREDS:
    print("::: No credentials found. Exiting... ")
    sys.exit(1)

credential = ServiceAccountCredentials.from_json_keyfile_name(
    CREDS,
    [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

client = gspread.authorize(credential)
gsheet = client.open("Sales As Code").sheet1


def get_sales_terms():
    """Get sales terms from Google Sheets. Picks one at random."""
    sales_terms = gsheet.col_values(1)[1:]
    sales_term_choice = random.choice(sales_terms)
    return sales_term_choice


def spongecase(term):
    output = ""
    for char in term:
        if random.randint(0, 1) == 1:
            output += char.upper()
        else:
            output += char.lower()
    return output


def talking():
    while True:
        answer = input("Is the rep still talking? (y/n) ").lower()
        if answer != "y":
            break
        print(spongecase(get_sales_terms() + "\n"))


if __name__ == "__main__":
    talking()
