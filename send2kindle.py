#!/usr/bin/env python3

# A dirty script to send PDFs to my personal Kindle.
# Credentials (email password, email addresses, etc, should be kept in a `.env` file.)

import os
import sys
import argparse
from halo import Halo
from dotenv import load_dotenv
from redmail import EmailSender
from pathlib import Path


if os.path.isfile('.env'):  # Checking if .env file exists
    from dotenv import load_dotenv
    load_dotenv('.env')  # importing .env file as a environment variable(s)


parser = argparse.ArgumentParser(description='Send a PDF to my Kindle.')
parser.add_argument('file', help='The file to be sent.')
parser.add_argument('-s', '--subject', default='Convert', help='The subject of the email.')
args = parser.parse_args()


# Building the email
email = EmailSender(
    host='smtp.office365.com',
    port=587,
    username=os.getenv('EMAIL_ADDRESS'),
    password=os.getenv('EMAIL_PASSWORD')
)

filename = os.path.basename(args.file)
attachment = open(os.path.abspath(args.file), "rb")

# Sending the email
@Halo(text='Sending email...', spinner='dots')
def send_email():
    email.send(
        sender=os.getenv('EMAIL_ADDRESS'),
        receivers=[os.getenv('KINDLE_ADDRESS')],
        subject=args.subject,
        attachments={
            filename: Path(args.file).read_bytes()
        }
    )

try:
    send_email()
    print(f"::: Sent {filename} to {os.getenv('KINDLE_ADDRESS')}")
except Exception as e:
    print(e)
    sys.exit(1)
