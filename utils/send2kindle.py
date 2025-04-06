#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "halo",
#     "python-dotenv",
#     "redmail",
# ]
# ///

"""
A script to send PDFs to a Kindle.
Credentials (email, password, Kindle address) are stored in a `.env` file.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from halo import Halo
from redmail import EmailSender

# Initialize logging
logging.basicConfig(level=logging.INFO)


def load_environment_variables(config_file: str) -> None:
    """Loads environment variables from the specified .env file."""
    if os.path.isfile(config_file):
        load_dotenv(config_file)
        required_env_vars = ["EMAIL_ADDRESS", "EMAIL_PASSWORD", "KINDLE_ADDRESS"]
        for var in required_env_vars:
            if not os.getenv(var):
                logging.error(f"Environment variable {var} is missing.")
                sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """Parses and validates command line arguments."""
    parser = argparse.ArgumentParser(description="Send a PDF to my Kindle.")
    parser.add_argument("file", help="The PDF file to be sent.")
    parser.add_argument(
        "-s", "--subject", default="Convert", help="The subject of the email.", type=str
    )
    parser.add_argument("-c", "--config", default=".env", help="The .env file to use.")
    args = parser.parse_args()

    # if not os.path.isfile(args.file) or not args.file.lower().endswith('.pdf'):
    #     logging.error("The specified file is not a valid PDF.")
    #     sys.exit(1)

    return args


def build_email(args: argparse.Namespace) -> tuple:
    """Constructs the email sender object."""
    email = EmailSender(
        host=os.getenv("SMTP_HOST", "smtp.office365.com"),
        port=int(os.getenv("SMTP_PORT", "587")),  # Convert default value to string
        username=os.getenv("EMAIL_ADDRESS"),
        password=os.getenv("EMAIL_PASSWORD"),
    )

    filename = os.path.basename(args.file)
    return email, filename


# Sending the email
@Halo(text="Sending email...", spinner="dots")
def send_email(email: EmailSender, filename: str, args: argparse.Namespace) -> None:
    """Sends the constructed email."""
    with Path(args.file).open(mode="rb") as file:
        email.send(
            sender=os.getenv("EMAIL_ADDRESS"),
            receivers=[os.getenv("KINDLE_ADDRESS")],
            subject=args.subject,
            attachments={filename: file.read()},
        )


def main():
    """Onto the actual sending..."""
    args = parse_arguments()
    load_environment_variables(args.config)

    try:
        email, filename = build_email(args)
        send_email(email, filename, args)
        logging.info(f"Sent {filename} to {os.getenv('KINDLE_ADDRESS')}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
