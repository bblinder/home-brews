#!/usr/bin/env python2

# Simple script to upload mp3's to my Google Music account. Uses the unofficial gmusic API.

from sys import argv
try:
	from gmusicapi import Musicmanager
except ImportError:
	print "Can't import gmusicapi - check that it's installed"
	print "Exiting..."
	sys.exit()

mm = Musicmanager()
## mm.perform_oauth() # For the first run/implementation only. Not needed afterwards.
mm.login()

track = argv
print track

def upload_music(track):
	mm.upload(track, enable_matching=True, enable_transcoding=True)

if __name__ == '__main__':
	upload_music(track)
