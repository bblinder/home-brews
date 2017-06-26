#!/usr/bin/env python

from twilio.rest import Client
import random

result = (random.choice(list(open('quotes'))))

account_sid = ""
auth_token = ""

client = Client(account_sid, auth_token))

client.messages.create(to="",
        from_="",
        body=result)

