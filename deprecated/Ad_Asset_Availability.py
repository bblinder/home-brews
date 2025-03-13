#!/usr/bin/env python

# a script to force availability of an asset living on a CDN. QAM VOD only.

api_token = '' # insert before flight
network_id = '' # insert before flight
HTTP_type = 'PUT'
file_name = 'pid_paid_pairs.csv' # ensure this file exists before running

legacy = 'legacy'
watermark = 'watermark'

import csv
import httplib # probably going to replace this with Requests at some point.
import time

"""
Going to hit both legacy and watermark stores simultaneously.
If only doing one, simply comment out the other function.
"""

def legacy_store():
	with open(file_name, 'U') as csvfile:
		csv_reader = csv.reader(csvfile)
		for row in csv_reader:
			value_from_csv = row[0]
			headers = {"Content-type": "application/xml", "Accept": "application/xml", "X-token": api_token}
			# need to specify which environment (prod or 'stg')
			# leaving it facing 'stg' by default.
			conn = httplib.HTTPSConnection('vapi.mydomain.com')
			url = "/services/ad_asset_store/%s" % (network_id)
			api_body = "<asset><tag>%s</tag><url><![CDATA[%s]]></url><available_percentage>100</available_percentage></asset>" % (legacy, value_from_csv)
			conn.request(HTTP_type, url, api_body, headers)
			response = conn.getresponse()
			print response.status, response.reason
			data = response.read()
			print data
			conn.close()
			time.sleep(1)

def watermark_store():
	with open(file_name, 'U') as csvfile:
		csv_reader = csv.reader(csvfile)
		for row in csv_reader:
			value_from_csv = row[0]
			headers = {"Content-type": "application/xml", "Accept": "application/xml", "X-token": api_token}
			# need to specify which environment (prod or 'stg')
			# leaving it facing 'stg' by default.
			conn = httplib.HTTPSConnection('vapi.mydomain.com')
			url = "/services/ad_asset_store/%s" % (network_id)
			api_body = "<asset><tag>%s</tag><url><![CDATA[%s]]></url><available_percentage>100</available_percentage></asset>" % (watermark, value_from_csv)
			conn.request(HTTP_type, url, api_body, headers)
			response = conn.getresponse()
			print response.status, response.reason
			data = response.read()
			print data
			conn.close()
			time.sleep(1)

if __name__ == '__main__':
	legacy_store()
	watermark_store()
