#!/usr/bin/env python

# Simple script to upload mp3's to my Google Music account. Uses the unofficial gmusic API.

from sys import argv
try:
	from gmusicapi import Musicmanager
except ImportError:
	print "Can't import gmusicapi - check that it's installed"
	print "Exiting..."
	sys.exit()

mm = Musicmanager()
#mm.perform_oauth() # Should be run for the first implementation only. Not needed afterwards.
mm.login()

track = argv
#print track

def upload_music(track):
	mm.upload(track, enable_matching=True)

if __name__ == '__main__':
	upload_music(track)
