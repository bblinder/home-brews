#!/usr/bin/env python3

# A dirty script to send PDFs to my personal Kindle.
# Credentials (gmail password, email addresses, etc, should be kept in a `.env` file.)

from ast import Sub
from re import sub
import sys
import os
from dotenv import load_dotenv

try:
    from halo import Halo
except ImportError:
    print("::: Halo (needed for progress bar) not installed ")
    print("::: Please install with: `pip install halo` ")
    sys.exit(1)

load_dotenv() # importing .env file as a environment variable(s)

# Mail stuff
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders, message
 
# I usually use a dummy/throwaway gmail account for this.
# Just be sure to whitelist it in your Amazon account under "Content and Devices" -> "Preferences" -> "Personal Document Settings"
fromaddr = os.getenv('GMAIL_ADDRESS')
gmail_password = os.getenv('GMAIL_PASSWORD')
toaddr = os.getenv('KINDLE_ADDRESS') # The Kindle's email address

fn = sys.argv[1] # the file to be sent (equivalent to "$1" in bash/zsh)
subject = sys.argv[2] # The subject of the email. Use "Convert" if you want Amazon to convert the PDF into a MOBI file, otherwise use whatever you like.
filename = os.path.basename(fn)
attachment = open(os.path.abspath(fn), "rb")

msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = subject

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
        sys.exit(1)
    sys.exit(0)
