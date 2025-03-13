#!/usr/bin/env python3

"""
A simple dictionary and thesaurus script, using the Oxford Dictionary API
"""

import argparse
import json
import os

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

parser = argparse.ArgumentParser()
parser.add_argument(
    "-e", "--endpoint", help="Get thesaurus results", default="entries", required=False
)
parser.add_argument("word", help="The word you want to look up")
parser.usage = """
thesaurus.py [-h] [-e ENDPOINT] word

The endpoint can be one of the following:
    - entries
    - thesaurus
"""

args = parser.parse_args()

if os.path.isfile(".env"):
    load_dotenv(".env")

app_id = os.getenv("APP_ID")
app_key = os.getenv("APP_KEY")
LANGUAGE = "en-us"
BASE_URL = "https://od-api.oxforddictionaries.com/api/v2"


def get_word(endpoint, word):
    """Making the API request, returning the results"""

    url = f"{BASE_URL}/{endpoint}/{LANGUAGE}/{word}"
    r = requests.get(url, headers={"app_id": app_id, "app_key": app_key}, timeout=5)
    results = json.dumps(r.json())
    return results


# def main():
#     endpoint = args.endpoint
#     word = args.word.lower()
#     results = get_word(endpoint, word)
#     print(json.dumps(json.loads(results), indent=4, sort_keys=True))


def main():
    """Taking the returned API result and printing it in a table with Rich"""

    endpoint = args.endpoint
    word = args.word.lower()
    results = get_word(endpoint, word)
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")

    if endpoint == "entries":
        table.add_column("Word", style="dim", width=12)
        table.add_column("Definition", style="dim", width=12)
        table.add_column("Example", style="dim", width=12)
        table.add_column("Synonyms", style="dim", width=20)

        for result in json.loads(results)["results"]:
            for lexical_entry in result["lexicalEntries"]:
                for entry in lexical_entry["entries"]:
                    for sense in entry["senses"]:
                        table.add_row(
                            result["word"],
                            sense["definitions"][0],
                            sense["examples"][0]["text"],
                            # return first 15 synonyms
                            ", ".join(
                                synonym["text"] for synonym in sense["synonyms"][:15]
                            ),
                        )

    elif endpoint == "thesaurus":
        table.add_column("Word", style="dim", width=12)
        table.add_column("Synonym", style="dim", width=20)

        for result in json.loads(results)["results"]:
            for lexical_entry in result["lexicalEntries"]:
                for entry in lexical_entry["entries"]:
                    for sense in entry["senses"]:
                        for synonym in sense["synonyms"]:
                            table.add_row(result["word"], synonym["text"])

    console.print(table)


if __name__ == "__main__":
    main()
