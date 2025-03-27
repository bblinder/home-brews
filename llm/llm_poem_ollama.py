#!/usr/bin/env python3

"""
Generate a haiku based on the current time using an Ollama model.
Requires an Ollama API key set as an environment variable.
"""

import datetime
import pytz
import os

try:
    from ollama import chat, ChatResponse
except ImportError:
    print("Please install the Ollama Python library: pip install ollama")
    raise

# Check for Ollama API key
ollama_api_key = os.getenv("OLLAMA_API_KEY")
if not ollama_api_key:
    raise EnvironmentError(
        "Please set your Ollama API key as an environment variable named OLLAMA_API_KEY."
    )


def get_time(time_zone=None):
    """
    Get the current time in a human-readable format.
    Optionally accepts a time zone. Returns formatted version.
    """
    try:
        now = (
            datetime.datetime.now(pytz.timezone(time_zone))
            if time_zone
            else datetime.datetime.now()
        )
        time_str = now.strftime("%I:%M")
        return time_str
    except Exception as e:
        print(f"Error getting time: {e}")
        raise


def generate_poem():
    """
    Generate a short poem using the LLM model.
    Uses the current time as an inspiration for the poem.
    """
    time_str = get_time()
    try:
        response: ChatResponse = chat(
            model="openthinker:latest",  # Replace with the appropriate Ollama model
            messages=[
                {
                    "role": "system",
                    "content": "You are a poetic assistant, skilled in explaining complex concepts with creative flair.",
                },
                {
                    "role": "user",
                    "content": f"Generate a very short one-stanza poem based on the time. Be imaginative and profound, incorporating the time: {time_str}. Output only the poem!",
                },
            ],
        )
        return response.message.content
    except Exception as e:
        print(f"Error in generating poem: {e}")
        raise


def format_poem(poem):
    """Format the poem to be more readable."""
    return poem.replace("\n", " / \n")


def main():
    try:
        poem = generate_poem()
        formatted_poem = format_poem(poem)
        print(formatted_poem)
    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    main()
