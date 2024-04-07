#!/usr/bin/env python3

"""
This script updates a Google Sheet with restaurant data from Google Maps.

Future TODOs:
- Add support for multiple sheets in the workbook
- Add Flask web interface for user to input restaurant data
- Add Flask endpoint to trigger the script
"""

import gspread
import googlemaps
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm  # Import tqdm for progress bar support

def load_env_variables():
    """Load environment variables from a .env file."""
    load_dotenv()  # This loads the environment variables from a .env file.
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    google_sheets_credential_path = os.path.expanduser(os.getenv('GOOGLE_SHEETS_CREDENTIAL_PATH'))
    return google_maps_api_key, google_sheets_credential_path

def init_clients(google_maps_api_key, google_sheets_credential_path):
    """Initialize and return Google Maps and Sheets clients."""
    gmaps = googlemaps.Client(key=google_maps_api_key)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(google_sheets_credential_path, scope)
    client = gspread.authorize(credentials)
    return gmaps, client

def update_google_sheet(sheet, gmaps):
    """Update Google Sheet with restaurant data from Google Maps."""
    data = sheet.get_all_values()
    headers = ["Restaurant Name", "Address", "Google Maps URL", "Date Added", "Notes"]
    if data[0] != headers:
        sheet.insert_row(headers, 1)
        data.insert(0, headers)

    # Initialize progress bar with tqdm
    progress = tqdm(enumerate(data[1:], start=2), total=len(data)-1, desc="Updating Restaurants Sheet")

    for i, row in progress:
        restaurant, address, maps_url, date_added, _ = (row + [None]*5)[:5]
        if not address or not maps_url:
            place_result = gmaps.places(query=restaurant)
            if place_result['results']:
                first_result = place_result['results'][0]
                new_address = first_result['formatted_address']
                place_id = first_result['place_id']
                new_google_maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                if not address:
                    sheet.update_cell(i, 2, new_address)
                if not maps_url:
                    sheet.update_cell(i, 3, new_google_maps_url)
                if not date_added:
                    sheet.update_cell(i, 4, datetime.now().strftime("%Y-%m-%d"))
            else:
                if not address:
                    sheet.update_cell(i, 2, "No address found")
                if not maps_url:
                    sheet.update_cell(i, 3, "No Google Maps URL found")

def main():
    """Handling our workflow"""
    google_maps_api_key, google_sheets_credential_path = load_env_variables()
    gmaps, client = init_clients(google_maps_api_key, google_sheets_credential_path)
    sheet = client.open('Maine Restaurants').sheet1
    update_google_sheet(sheet, gmaps)
    print("\nDone Updating Restaurants Sheet!")

if __name__ == '__main__':
    main()
