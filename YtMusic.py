#!/usr/bin/env python3

# derived from: https://ytmusicapi.readthedocs.io/
# See "Setup" on how to get auth headers.

import sys, os
from pprint import pprint

try:
    from ytmusicapi import YTMusic
except ImportError:
    print("::: Can't import ytmusicapi - check that it's installed")
    print("::: Exiting...")
    sys.exit(1)

authFile = 'headers_auth.json'
ytmusic = YTMusic(authFile)

d = sys.argv[1] # track or music directory

def upload(track):
    print(track)
    filesize = os.path.getsize(track)
    print('Size of track: ' + str(filesize) + ' ' + 'bytes')
    ytmusic.upload_song(track)
        

def main(d):
    if os.path.isfile(d):
        track = d
        filesize = os.path.getsize(track)
        upload(track)
    elif os.path.isdir(d):
        for path in os.listdir(d):
            full_path = os.path.join(d, path)
            track = full_path
            upload(track)
    else:
        print("No track or music folder specificed")
        sys.exit(1)
    
main(d)