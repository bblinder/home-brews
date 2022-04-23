import os

# Lambda function to "Clear" the terminal
clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')
# clear()

def get_downloads_folder():
    if os.name == 'nt':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')

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
