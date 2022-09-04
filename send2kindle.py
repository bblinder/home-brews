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

parser = argparse.ArgumentParser(description='Send a PDF to my Kindle.')
parser.add_argument('file', help='The file to be sent.')
parser.add_argument('-s', '--subject', default='Convert', help='The subject of the email.', type=str)
parser.add_argument('-c', '--config', default='.env', help='The .env file to use.', required=False)
args = parser.parse_args()

if os.path.isfile(args.config):
    load_dotenv(args.config)


def build_email():
# Building the email
    email = EmailSender(
        host='smtp.office365.com',
        port=587,
        username=os.getenv('EMAIL_ADDRESS'),
        password=os.getenv('EMAIL_PASSWORD')
    )

    filename = os.path.basename(args.file)
    return email, filename

# Sending the email
@Halo(text='Sending email...', spinner='dots')
def send_email(email, filename):
    email.send(
        sender=os.getenv('EMAIL_ADDRESS'),
        receivers=[os.getenv('KINDLE_ADDRESS')],
        subject=args.subject,
        attachments={
            filename: Path(args.file).read_bytes()
        }
    )

try:
    email, filename = build_email()
    send_email(email, filename)
    print(f"::: Sent {filename} to {os.getenv('KINDLE_ADDRESS')}")
except Exception as e:
    print(e)
    sys.exit(1)
