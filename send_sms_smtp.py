#!/usr/bin/env python

import random
import smtplib
import time
#from time import gmtime, strftime, localtime

# Credentials (if needed)
# A new gmail account is recommended for this
username = '[your username]'
password = '******'
fromaddr = '[your username]@gmail.com'
toaddrs  = 'yournumber@yoursmsgateway'

# Picking a random line from 'quotes.txt', assuming it exists
random_quote = (random.choice(list(open('quotes.txt'))))

#subject = "For you, a word..."
subject = random_quote
message = 'Subject: {}\n\n{}'.format(subject, subject)
# The actual mail send
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)
server.sendmail(fromaddr, toaddrs, message)
server.quit()
