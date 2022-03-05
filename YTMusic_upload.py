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

try:
    from halo import Halo
except ImportError:
    print("::: Halo not installed - please install with: ")
    print("::: 'pip install halo' ")
    print("::: Exiting... ")
    sys.exit(1)

authFile = 'headers_auth.json' # You need to create this ahead of time.

if os.path.isfile(authFile):
    ytmusic = YTMusic(authFile)
else:
    print("::: " + authFile + " does not exist...")
    sys.exit(1)
#d = sys.argv[1] # track or music directory

def convert_bytes(bytes_number):
    tags = [ "Bytes", "KB", "MB", "GB", "TB" ]
 
    i = 0
    double_bytes = bytes_number
 
    while (i < len(tags) and  bytes_number >= 1024):
            double_bytes = bytes_number / 1024.0
            i = i + 1
            bytes_number = bytes_number / 1024
 
    return str(round(double_bytes, 2)) + " " + tags[i]
 

@Halo(text="Uploading...", spinner='dots')
def upload(track):
    print(track)
    filesize = os.path.getsize(track)
    print('Size of track: ' + convert_bytes(filesize) + ' ')
    ytmusic.upload_song(track)
        

def main(track):
    if os.path.isfile(track):
        filesize = os.path.getsize(track)
        upload(track)
    elif os.path.isdir(track):
        for path in os.listdir(track):
            full_path = os.path.join(track, path)
            track = full_path
            upload(track)
    else:
        print("No track or music folder specificed")
        sys.exit(1)
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="This script uploads a music track or directory of tracks to YouTube Music")
    parser.add_argument("track", help="The path to the track or directory to upload")
    
    args = parser.parse_args()
    track = args.track
    main(track)
