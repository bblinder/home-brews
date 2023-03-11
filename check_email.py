#!/usr/bin/env python3

"""Check email address for validity and suggest changes if invalid"""

from email_validator import EmailNotValidError, validate_email
from rich.console import Console

console = Console()


def suggest_changes(email):
    """Suggest syntax changes to email address"""

    suggestions = []
    if "@" not in email:
        suggestions.append("::: add @")
    if "." not in email:
        suggestions.append("::: add .")
    if " " in email:
        suggestions.append("::: remove spaces")
    if ".co" in email:
        suggestions.append("::: Try changing .co to .com")
    if suggestions:
        console.print("Suggestions:", style="bold")
        for suggestion in suggestions:
            console.print(f"  {suggestion}", style="bold")
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
        suggest_changes(email)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="email address")
    args = parser.parse_args()
    main()
