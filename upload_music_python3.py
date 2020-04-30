#!/usr/bin/env python3

# Simple script to upload mp3's to my Google Music account. Uses the unofficial gmusic API.

import sys
from sys import argv
import random
try:
	from gmusicapi import Musicmanager
except ImportError:
	print ("Can't import gmusicapi - check that it's installed")
	print ("Exiting...")
	sys.exit()

# A unique id as a MAC address, eg '00:11:22:33:AA:BB'. 
# Per the docs, this should only be provided in cases where the default (host MAC address incremented by 1) will not work.
mac_address = '38:F9:D3:57:68:FC'

mm = Musicmanager()
# mm.perform_oauth() # For the first run/implementation only. Not needed afterwards.
mm.login(uploader_id=mac_address)

''' For later, when I'm generating a random MAC address
def rand_mac():
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
        )
'''

track = argv
print(track)

def upload_music(track):
	mm.upload(track, enable_matching=True, enable_transcoding=True)

if __name__ == '__main__':
    upload_music(track)
    mm.logout(revoke_oauth=False)
