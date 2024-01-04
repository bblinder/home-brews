#!/usr/bin/env python3

"""Generate a haiku based on the current time using an OpenAI model."""

import datetime
from openai import OpenAI
client = OpenAI()

# check for OpenAI API key
if not client.api_key:
  raise Exception("Please set your OpenAI API key as an environment variable named OPENAI_API_KEY.")

def get_time():
  """Get the current time in a human-readable format and return formatted version."""
  time_str = datetime.datetime.now().strftime("%I:%M")
  # Format for bold and blue text (ANSI escape codes)
  formatted_time = f"\033[1;34m{time_str}\033[0m"
  return time_str, formatted_time

def generate_poem():
  """Generate a short poem using the LLM model."""
  time = get_time()
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
      {"role": "user", "content": "Generate a very short one-stanza poem based on the time. Be imaginative and profound, incorporating the time: " + time[1]},
    ]
  )
  return completion.choices[0].message.content  # Get the 'content' of the message using dot notation

def format_poem(poem):
  """Format the poem to be more readable."""
  return poem.replace("\n", " / \n")

def main():
  poem = generate_poem()
  formatted_poem = format_poem(poem)  # Now poem is a string
  print(formatted_poem)

if __name__ == "__main__":
  main()