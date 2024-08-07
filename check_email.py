#!/usr/bin/env python3

"""A small utility to check email address for validity"""

import re
import argparse
from email_validator import EmailNotValidError, validate_email
from rich.console import Console

console = Console()


def suggest_changes(email):
    """Suggest syntax changes to email address using regex"""

    suggestions = []
    if "@" not in email:
        suggestions.append("::: add @")
    if "." not in email:
        suggestions.append("::: add .")
    if " " in email:
        suggestions.append("::: remove spaces")
    if ".co" in email:
        suggestions.append("::: Try changing .co to .com")
    if ".io" in email and ".com" not in email:
        suggestions.append("::: Try changing .io to .com")
    if ".me" in email and ".com" not in email:
        suggestions.append("::: Try changing .me to .com")
    if ".us" in email and ".com" not in email:
        suggestions.append("::: Try changing .us to .com")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        suggestions.append("::: Invalid format, please check your email address")
    if len(suggestions) > 0:
        return suggestions
    else:
        return None


def validate_address(email):
    """Uses the email-validator package to screen email address"""

    try:
        email = validate_email(email, check_deliverability=True).email
        console.print(f"{email} is valid", style="bold green")
        return email
    except EmailNotValidError as err:
        console.print(f"{email} is invalid", style="bold red")
        console.print(err, style="bold red")
        return None


def main():
    """Checks email address and suggests changes if invalid"""

    email = args.email.strip()
    if validate_address(email) is None:
        suggestions = suggest_changes(email)
        if suggestions:
            console.print("Suggestions:", style="bold")
            for suggestion in suggestions:
                console.print(f"  {suggestion}", style="bold")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="email address")
    args = parser.parse_args()
    main()
