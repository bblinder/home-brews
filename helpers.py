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


def bootstrap_venv():
    """Bootstraps a Python virtual environment.

    Args:
        venv_dir (str): The directory of the virtual environment. Defaults to 'venv'.
        requirements_file (str): Path to a requirements.txt file. Defaults to 'requirements.txt'.

    Requires:
        - Pathlib
    """
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / "venv"
    venv_python = venv_dir / "bin" / "python"

    if not venv_dir.exists():
        print("No virtual environment found. Setting one up...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print(f"Virtual environment created at {venv_dir}")
    else:
        print(f"Virtual environment already exists at {venv_dir}")

    if sys.executable != str(venv_python):
        print(f"Activating virtual environment at {venv_dir}")
        os.execv(str(venv_python), [str(venv_python), *sys.argv])

    print(f"Using virtual environment at {venv_dir}")

    requirements_path = script_dir / "requirements.txt"
    if requirements_path.exists():
        print("Installing dependencies from requirements.txt...")
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements_path)],
            check=True,
        )
    else:
        print("requirements.txt not found, skipping dependency installation.")
