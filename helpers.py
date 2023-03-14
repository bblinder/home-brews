import os

# Lambda function to "Clear" the terminal
clear = lambda: os.system("cls" if os.name == "nt" else "clear")


def get_downloads_folder():
    if os.name == "nt":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# Convert bytes depending on file size
def convert_bytes(bytes_number):
    tags = ["Bytes", "KB", "MB", "GB", "TB"]

    i = 0
    double_bytes = bytes_number

    while i < len(tags) and bytes_number >= 1024:
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


def spongecase(term):
    output = ""
    for char in term:
        if random.randint(0, 1) == 1:
            output += char.upper()
        else:
            output += char.lower()
    return output


def deal_with_it():
    from time import sleep

    print("( •_•) ")
    sleep(0.75)
    print("\r( •_•)>⌐■-■")
    sleep(0.75)
    print("\r               ")
    print("\r(⌐■_■)")
    sleep(0.5)


# Generate random MAC address
def generate_mac():
    import random

    mac = [
        0x00,
        0x16,
        0x3E,
        random.randint(0x00, 0x7F),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
    ]
    return ":".join(map(lambda x: "%02x" % x, mac))
