#!/usr/bin/env python3

# Lambda function to "Clear" the terminal
'''
clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')
clear()
'''

# Convert bytes depending on file size
def convert_bytes(bytes_number):
    tags = [ "Bytes", "KB", "MB", "GB", "TB" ]
  
    i = 0
    double_bytes = bytes_number
  
    while (i < len(tags) and  bytes_number >= 1024):
            double_bytes = bytes_number / 1024.0
            i = i + 1
            bytes_number = bytes_number / 1024
  
    return str(round(double_bytes, 2)) + " " + tags[i]

def check_valid_url(url):
    try:
        import validators
    except ImportError:
        print("Please install validators module")
        return False
    return validators.url(url)