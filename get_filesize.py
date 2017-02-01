#/usr/bin/env python

import os

cur_dir = os.getcwd()
get_summary = sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))

def get_files(dirname, reverse=True):
    # Getting our list of files
    filepaths = []
    for basename in os.listdir(dirname):
        filename = os.path.join(dirname, basename)
        if os.path.isfile(filename):
            filepaths.append(filename)

    for i in xrange(len(filepaths)):
        filepaths[i] = (filepaths[i], os.path.getsize(filepaths[i]))

    # Sorting our list by file size, largest to smallest
    filepaths.sort(key=lambda filename: filename[1], reverse=reverse)

    return filepaths
print "Total Size: ", get_summary, "bytes"
print get_files(cur_dir)

#########################################################

# A slightly quicker, but messier, method
"""
import os

cur_dir = os.getcwd()
d = os.listdir(cur_dir)

print "Total Size: ", sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f)), "bytes"

for x in d:
	print x, os.path.getsize(x), "bytes"
"""
