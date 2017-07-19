#!/usr/bin/env python2

# Queries a list of zip codes (CSV) against the SmartyStreets API

auth_id = "" # Insert before flight
auth_token = "" # Insert before flight
HTTP_type = 'GET'
file_name = "" # Insert before flight. Should be living in the same directory as this script

import csv
import time
try :
    import requests # Finally!
except ImportError:
    print "Can't import Requests -- check that it's installed!"
    print "Exiting..."
    sys.exit(1)

def zip_request():
    with open(file_name, 'U') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            value_from_csv = row[0]
            #headers = {"content-type": "application/json"}
            url = "https://us-zipcode.api.smartystreets.com/lookup?auth-id=%s&auth-token=%s&zipcode=%s" % (auth_id, auth_token, value_from_csv)
            r = requests.get(url)
            print r.json()

# Now doing the actual work...
if __name__ == '__main__':
    zip_request()
