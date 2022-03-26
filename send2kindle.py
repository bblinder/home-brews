#!/usr/bin/env python3

# A dirty script to send PDFs to my personal Kindle.
# Credentials (gmail password, email addresses, etc, should be kept in a `.env` file.)

import os
try:
    from halo import Halo
except ImportError:
    print("::: Halo (needed for progress bar) not installed ")
    print("::: Please install with: `pip install halo` ")
    exit(1)

if os.path.isfile('.env'): # Checking if .env file exists
    from dotenv import load_dotenv
    load_dotenv() # importing .env file as a environment variable(s)

# arguments
import argparse
parser = argparse.ArgumentParser(description='Send a PDF to my Kindle.')
parser.add_argument('file', help='The file to be sent.')
parser.add_argument('subject', default='Convert', help='The subject of the email.')
args = parser.parse_args()

# Mail stuff
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders, message
 
# I usually use a dummy/throwaway gmail account for this.
# Just be sure to whitelist it in your Amazon account under "Content and Devices" -> "Preferences" -> "Personal Document Settings"
fromaddr = os.environ['GMAIL_ADDRESS']
gmail_password = os.environ['GMAIL_PASSWORD']
toaddr = os.environ['KINDLE_ADDRESS'] # The Kindle's email address

filename = os.path.basename(args.file)
attachment = open(os.path.abspath(args.file), "rb")
    
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = args.subject # Subject of the email
body = "New Doc"

# Now onto the actual work...
def build_email():
    msg.attach(MIMEText(body, 'plain'))
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    
    msg.attach(part)

@Halo(text="Uploading file...", spinner='dots')
def send_email():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, gmail_password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

if __name__ == "__main__":
    build_email()
    try:
        send_email()
    except:
        print("::: Error. Could not be sent.")
        exit(1)
    exit()
