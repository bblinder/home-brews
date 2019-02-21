#!/usr/bin/env python

# A dirty script to send PDFs to my personal Kindle.
# Probably going to have to be rewritten once Python 2 goes away.

import sys
import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
 
# I usually use a dummy/throwaway gmail account for this.
# Just be sure to whitelist it in your Amazon account under "Content and Devices" -> "Preferences" -> "Personal Document Settings"
fromaddr = "SENDING-FROM-THIS-EMAIL"
toaddr = "RECEIVING-AT-THIS-EMAIL" # The Kindle's email address
 
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Custom PDF"

body = "New PDF"

fn = sys.argv[1]
filename = os.path.basename(fn)
attachment = open(os.path.abspath(fn), "rb")

# Now onto the actual work...
def build_email():
    msg.attach(MIMEText(body, 'plain'))
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    
    msg.attach(part)

def send_email():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "your-gmail-password")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

if __name__ == "__main__":
    build_email()
    send_email()
    sys.exit(0)
