#!/usr/bin/env python2

import requests
from bs4 import BeautifulSoup
import os

URL = "" # Insert before flight

r = requests.get(URL)
data = r.text
soup = BeautifulSoup(data, "lxml")

#handle = open("wb")

"""
for chunk in resp.iter_content(chunk_size=512):
    if chunk:
        handle.write(chunk)
"""
for link in soup.find_all('img'):
    image = link.get("data-image")
    print(image)



"""
def requests_image(URL):
    suffix_list = ['jpg', 'gif', 'png', 'tif', 'svg',]
    file_name = urlsplit(URL)[2].split('/')[-1]
    file_suffix = file_name.split('.')[1]
    i = requests.get(URL)
    if i.status.code == requests.codes.ok:
        with iopen(file_name, 'wb') as file:
            file.write(i.content)
"""