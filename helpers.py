import os
import sys

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
    import random

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


def generate_qr_code(data):
    """Generate a QR code image from the provided data and save it to the output file."""
    try:
        import qrcode
    except ImportError:
        print("qrcode not installed")
        sys.exit(1)

    try:
        import urllib.parse
    except ImportError:
        print("urllib.parse not installed")
        sys.exit(1)

    def name_the_output_file(data):
        """Create a sanitized output file name based on the provided data."""

        # Parse the input data as a URL
        parsed_data = urllib.parse.urlparse(data)

        # Use the path component of the URL
        path = parsed_data.path if parsed_data.path else data

        # Use the basename of the path as the output file name
        output = os.path.basename(path)

        # Set a default file name if the output is empty
        if not output:
            output = "output"

        return output

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)

    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    output = f"{name_the_output_file(data)}.png"

    img.save(output)


def restore_punctuation(text):
    """Restore punctuation to a string/transcript"""
    try:
        from deepmultilingualpunctuation import PunctuationModel
    except ImportError:
        print("deepmultilingualpunctuation not installed")
        sys.exit(1)
    model = PunctuationModel()
    return model.restore_punctuation(text)


def bootstrap_venv(venv_dir="venv", requirements_file="requirements.txt"):
    """Bootstraps a Python virtual environment.

    Args:
        venv_dir (str): The directory of the virtual environment. Defaults to 'venv'.
        requirements_file (str): Path to a requirements.txt file. Defaults to 'requirements.txt'.
    """
    import subprocess
    
    SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
    VENV_DIR = os.path.join(SCRIPT_DIR, venv_dir)
    IS_WINDOWS = sys.platform.startswith("win")
    VENV_BIN_DIR = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin")
    VENV_ACTIVATE_BASH = os.path.join(VENV_BIN_DIR, "activate")
    REQUIREMENTS_PATH = os.path.join(SCRIPT_DIR, requirements_file)
    PYTHON_EXECUTABLE = os.path.join(
        VENV_BIN_DIR, "python3.exe" if IS_WINDOWS else "python3"
    )

    if not os.path.exists(VENV_DIR):
        print("No virtual environment found. Setting one up...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        print("Virtual environment created at {}".format(VENV_DIR))

    if "VIRTUAL_ENV" not in os.environ:
        if IS_WINDOWS:
            command = '"{}" && "{}" "{}" {}'.format(
                VENV_ACTIVATE_BASH, PYTHON_EXECUTABLE, __file__, " ".join(sys.argv[1:])
            )
            subprocess.check_call(command, shell=True)
        else:
            command = 'source "{}" && "{}" "{}" {}'.format(
                VENV_ACTIVATE_BASH,
                PYTHON_EXECUTABLE,
                __file__,
                " ".join(map(lambda x: '"{}"'.format(x), sys.argv[1:])),
            )
            os.execle("/bin/bash", "bash", "-c", command, os.environ)
        sys.exit()
    else:
        if os.path.exists(REQUIREMENTS_PATH):
            print("Installing dependencies from requirements.txt...")
            subprocess.check_call(
                [
                    PYTHON_EXECUTABLE,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    REQUIREMENTS_PATH,
                    "--upgrade",
                ],
                cwd=SCRIPT_DIR,
            )
        else:
            print("requirements.txt not found, skipping dependency installation.")