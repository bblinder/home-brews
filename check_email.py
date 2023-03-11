#!/usr/bin/env python3

from email_validator import EmailNotValidError, validate_email
from rich.console import Console

console = Console()


def suggest_changes(email):
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
        console.print("::: No suggestions", style="bold")


def validate_email_address(email):
    try:
        email = validate_email(email, check_deliverability=True).email
        console.print(f"{email} is valid", style="bold green")
        return email
    except EmailNotValidError as e:
        console.print(f"{email} is invalid", style="bold red")
        suggest_changes(email)


def main():
    email = args.email
    validate_email_address(email)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="email address")
    args = parser.parse_args()
    main()
