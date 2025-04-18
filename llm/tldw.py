#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests", "youtube_transcript_api"]
# ///

"""
TLDW (Too Long; Didn't Watch)
==============================

A standalone command-line tool for summarizing YouTube videos using local LLMs via Ollama.

This script extracts transcripts from YouTube videos, processes them using
locally hosted language models through Ollama, and generates structured summaries
with varying levels of detail.

Features:
- YouTube video transcript extraction using youtube_transcript_api
- Local LLM-powered summarization using Ollama
- Structured output with paragraph, sentence, question, and concise answer formats
- Wikipedia search term generation
- Result caching for faster repeat queries
- Command-line interface with various options

Original concept inspired by Stanley Tong's (stong) TLDW:
https://github.com/stong/tldw

This standalone version uses Ollama for local model inference
instead of relying on cloud APIs, providing privacy, cost savings,
and offline capability.

Usage (first make executable with chmod +x tldw.py):
  ./tldw.py [YouTube URL] [options]

Options:
  -o, --output       Output file path for saving results
  -t, --transcript-only  Only fetch and print the transcript
  --model            Specify Ollama model to use
  --host             Specify Ollama host URL
  --no-cache         Force regeneration, ignore existing cache

Requirements:
  - Ollama (https://ollama.com) running locally
  - At least one language model pulled in Ollama (e.g., mistral-nemo)
  - Python dependencies: requests, youtube_transcript_api


TODO:
    - implement chunking for long videos
    - better output parsing
    - temperature override flag
    - fetch video metadata for better grounding
"""

import argparse
import os
import sys
import requests
import json
from urllib.parse import quote_plus
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# --- Configuration ---
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
# Choose a model you have pulled with Ollama. More capable models might handle multi-step instructions better.
DEFAULT_OLLAMA_MODEL = "mistral-nemo:latest"
DEFAULT_TEMPERATURE = 0.0 # Default temperature for deterministic output

# Determine script directory and set cache directory within it
try:
    # Get the absolute path of the directory containing the script
    SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
except NameError:
    # Fallback if __file__ is not defined (e.g., running interactively)
    SCRIPT_DIR = os.path.abspath(os.getcwd())
    print(f"Warning: __file__ not defined. Using current working directory for cache: {SCRIPT_DIR}", file=sys.stderr)

# Use a specific subdirectory name within the script's directory for the cache
CACHE_SUBDIR = ".tldw_cache"
CACHE_DIR = os.path.join(SCRIPT_DIR, CACHE_SUBDIR)

# --- Helper Functions ---

def ensure_cache_dir():
    """Creates the cache directory if it doesn't exist."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except OSError as e:
        print(f"Warning: Could not create cache directory {CACHE_DIR}: {e}", file=sys.stderr)

def get_video_id(url):
    """Extracts the YouTube video ID from various URL formats."""
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0].split("&")[0]
    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    if "embed/" in url:
        return url.split("embed/")[1].split("?")[0].split("&")[0]
    if "/shorts/" in url:
         return url.split("/shorts/")[1].split("?")[0].split("&")[0]
    # Add more patterns if needed
    raise ValueError(f"Cannot parse YouTube Video ID from URL: {url}")

def get_transcript(video_id):
    """Fetches and formats the transcript."""
    print(f"Fetching transcript for video ID: {video_id} ...")
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_manually_created_transcript(['en'])
        print("Using manual English transcript.")
    except Exception:
        try:
            print("Manual English transcript not found or failed, trying generated English...")
            transcript = transcript_list.find_generated_transcript(['en'])
            print("Using generated English transcript.")
        except Exception as e:
            print(f"\nError: Could not fetch transcript for video ID {video_id}.", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            # Attempt to list available languages
            try:
                langs = [t.language for t in YouTubeTranscriptApi.list_transcripts(video_id)]
                print(f"Available transcript languages might be: {langs}", file=sys.stderr)
            except Exception:
                 print("Could not list available languages.", file=sys.stderr)
            sys.exit(1)

    formatter = TextFormatter()
    full_transcript = formatter.format_transcript(transcript.fetch())
    return full_transcript

def _ollama_chat_completion(messages, model_name, host_url, timeout=180, temperature=DEFAULT_TEMPERATURE):
    """Sends a full message history to the Ollama chat endpoint with temperature control."""
    api_url = f"{host_url.rstrip('/')}/api/chat"
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "temperature": temperature, # Add temperature to the payload
        # The 'options' dictionary can also be used for parameters if preferred/needed for other settings
        # "options": {
        #     "temperature": temperature
        # }
    }
    response = None # Initialize response to None
    try:
        # Debug print for payload
        # print(f"DEBUG: Sending payload to {api_url}: {json.dumps(payload, indent=2)}")
        response = requests.post(api_url, json=payload, timeout=timeout)
        response.raise_for_status() # Check for HTTP errors
        response_data = response.json()

        # Extract content based on expected Ollama API response structure
        if 'message' in response_data and 'content' in response_data['message']:
            return response_data['message']['content'].strip()
        elif 'response' in response_data: # Fallback for potential variations
             print("Warning: Received response in older format ('response' key).", file=sys.stderr)
             return response_data['response'].strip()
        else:
            # Log the unexpected format for debugging
            print(f"Error: Unexpected Ollama response format. Data: {response_data}", file=sys.stderr)
            return None
    except requests.exceptions.Timeout:
        print(f"\nError: Request to Ollama timed out after {timeout} seconds.", file=sys.stderr)
        return None
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to Ollama API at {api_url}. Is Ollama running?", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        # Handles HTTP errors (4xx, 5xx) after raise_for_status and other request issues
        print(f"\nError communicating with Ollama API at {api_url}: {e}", file=sys.stderr)
        if response is not None: # Check if response exists before accessing .text
             print(f"Response body: {response.text}", file=sys.stderr)
        return None
    except KeyError:
        # This might happen if the JSON response is valid but missing expected keys
        print(f"\nError parsing Ollama response structure. Raw response: {response.text if response is not None else 'No response object'}", file=sys.stderr)
        return None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"\nAn unexpected error occurred during Ollama chat completion: {e}", file=sys.stderr)
        return None

def get_structured_summary(video_id, transcript_text, model_name, host_url, ignore_cache=False):
    """
    Generates multiple summaries using Ollama, managing conversation history and caching.
    Returns a dictionary with summary parts or None if the first step fails.
    Uses the default temperature set in _ollama_chat_completion unless overridden.
    """
    cache_file = os.path.join(CACHE_DIR, video_id + '.summaries.json')

    if not ignore_cache and os.path.isfile(cache_file):
        try:
            print(f'Using cached summaries: {cache_file}')
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read cache file {cache_file}: {e}. Regenerating.", file=sys.stderr)
            try:
                 os.remove(cache_file)
            except OSError:
                 pass

    print("\n--- Generating Summaries ---")
    summaries = {}
    messages = [
        {"role": "system", "content": "You are an AI assistant specialized in analyzing video transcripts. Follow instructions precisely and provide only the requested output for each step."},
        {"role": "user", "content": f"Summarize the key points from the following video transcript into a single, concise paragraph. Focus on the main arguments, findings, or the core message presented in the text. PROVIDE NO OTHER OUTPUT OTHER THAN THE PARAGRAPH.\n\nTranscript:\n``````{transcript_text}``````"},
    ]

    print("1. Generating paragraph summary...")
    # Calls will now use the default temperature=0.0 unless explicitly overridden here
    paragraph_summary = _ollama_chat_completion(messages, model_name, host_url)
    if not paragraph_summary:
        print("Failed to generate initial paragraph summary. Aborting.", file=sys.stderr)
        return None
    summaries['paragraph'] = paragraph_summary
    messages.append({"role": "assistant", "content": paragraph_summary})

    print("2. Generating sentence summary...")
    messages.append({"role": "user", "content": "Now, based *only* on the transcript content provided earlier, condense the absolute core message or main takeaway into a single sentence. PROVIDE NO OTHER OUTPUT OTHER THAN THE SENTENCE."})
    sentence_summary = _ollama_chat_completion(messages, model_name, host_url)
    if not sentence_summary:
        sentence_summary = "[Error generating sentence summary]"
    summaries['sentence'] = sentence_summary
    messages.append({"role": "assistant", "content": sentence_summary})

    print("3. Generating question...")
    messages.append({"role": "user", "content": "Based *only* on the transcript content discussed so far, formulate a single question that effectively captures the main TOPIC or SUBJECT addressed. PROVIDE NO OTHER OUTPUT OTHER THAN THE QUESTION."})
    question = _ollama_chat_completion(messages, model_name, host_url)
    if not question:
        question = "[Error generating question]"
    summaries['question'] = question
    messages.append({"role": "assistant", "content": question})

    print("4. Generating concise answer...")
    question_prompt = question.replace('"', "'")
    messages.append({"role": "user", "content": f'Provide a very concise answer (ideally one or two words, max a short phrase) to the question "{question_prompt}", based *only* on the transcript content. Examples: "Is X true?" -> "Yes."/"No."/"Maybe."; "Why did Y happen?" -> "Reason Z."/"It\'s complex.". PROVIDE NO OTHER OUTPUT OTHER THAN THE CONCISE ANSWER.'})
    word_answer = _ollama_chat_completion(messages, model_name, host_url)
    if not word_answer:
        word_answer = "[Error generating answer]"
    summaries['word_raw'] = word_answer
    messages.append({"role": "assistant", "content": word_answer})

    print("5. Generating Wikipedia search term...")
    messages.append({"role": "user", "content": 'Suggest a specific and concise search term for Wikipedia that best represents the main TOPIC discussed in the transcript. Examples: "Discussion about AI replacing jobs" -> "Technological unemployment"; "History of the Eiffel Tower construction" -> "Eiffel Tower". PROVIDE NO OTHER OUTPUT OTHER THAN THE SEARCH TERM ITSELF.'})
    wiki_term = _ollama_chat_completion(messages, model_name, host_url)
    if not wiki_term:
        wiki_term = "[Error generating term]"
    messages.append({"role": "assistant", "content": wiki_term})

    summaries['word'] = f"{word_answer} ({wiki_term})" if not ('[Error' in word_answer or '[Error' in wiki_term) else word_answer
    summaries['wikipedia_url'] = 'https://en.wikipedia.org/w/index.php?search=' + quote_plus(wiki_term if '[Error' not in wiki_term else "")
    summaries['wikipedia_term'] = wiki_term

    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, indent=4, ensure_ascii=False)
        print(f'\nSummaries saved to cache: {cache_file}')
    except IOError as e:
        print(f"\nWarning: Could not write cache file {cache_file}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"\nWarning: An unexpected error occurred writing cache file {cache_file}: {e}", file=sys.stderr)

    return summaries

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(
        description="Generate structured summaries (paragraph, sentence, question, answer, Wikipedia term) of YouTube video transcripts using a local Ollama instance.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Show defaults in help
    )
    parser.add_argument("url", help="YouTube video URL (e.g., 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')")
    parser.add_argument("-o", "--output",
                        help="Output file path to save the structured summary as JSON (e.g., 'my_summary.json'). If directory, saves as {CACHE_DIR}/{video_id}.summaries.json")
    parser.add_argument("-t", "--transcript-only", action="store_true",
                        help="Only fetch and print the transcript, then exit.")
    parser.add_argument("--model", default=os.environ.get('OLLAMA_MODEL', DEFAULT_OLLAMA_MODEL),
                        help="Ollama model to use (or set OLLAMA_MODEL env var)")
    parser.add_argument("--host", default=os.environ.get('OLLAMA_HOST', DEFAULT_OLLAMA_HOST),
                        help="Ollama host URL (or set OLLAMA_HOST env var)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Force regeneration, ignore and overwrite existing cache file for this video.")
    # Could add an argument to override temperature if desired:
    # parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE,
    #                     help="Set the generation temperature (0.0 for deterministic).")

    args = parser.parse_args()

    ensure_cache_dir()

    try:
        video_id = get_video_id(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
         print(f"An unexpected error occurred parsing the URL '{args.url}': {e}", file=sys.stderr)
         sys.exit(1)

    print(f"Processing Video ID: {video_id}")

    transcript_text = get_transcript(video_id)

    if args.transcript_only:
        print("\n--- Transcript ---")
        print(transcript_text)
        if args.output:
             transcript_outfile = args.output if not os.path.isdir(args.output) else os.path.join(args.output, f"{video_id}.transcript.txt")
             try:
                 os.makedirs(os.path.dirname(transcript_outfile), exist_ok=True)
                 with open(transcript_outfile, "w", encoding="utf-8") as f:
                     f.write(transcript_text)
                 print(f"\nTranscript saved to {transcript_outfile}")
             except IOError as e:
                 print(f"Error writing transcript to file {transcript_outfile}: {e}", file=sys.stderr)
        sys.exit(0)

    structured_summaries = get_structured_summary(
        video_id,
        transcript_text,
        args.model,
        args.host,
        ignore_cache=args.no_cache
        # If --temperature arg was added: pass args.temperature to _ollama_chat_completion calls if needed
    )

    if structured_summaries:
        print("\n--- Final Structured Summary ---")
        keys_to_print = ['paragraph', 'sentence', 'question', 'word', 'wikipedia_term', 'wikipedia_url']
        for key in keys_to_print:
            if key in structured_summaries:
                 value = structured_summaries[key]
                 if isinstance(value, str):
                      value = value.strip('\'" ')
                 print(f"{key.replace('_', ' ').capitalize():<18}: {value}")

        if args.output:
            json_outfile = args.output
            if os.path.isdir(json_outfile):
                 json_outfile = os.path.join(CACHE_DIR, f"{video_id}.summaries.json")
            try:
                os.makedirs(os.path.dirname(json_outfile), exist_ok=True)
                with open(json_outfile, 'w', encoding='utf-8') as f:
                     json.dump(structured_summaries, f, indent=4, ensure_ascii=False)
                print(f"\nStructured summary also saved to: {json_outfile}")
            except Exception as e:
                print(f"\nError saving structured summary to {json_outfile}: {e}", file=sys.stderr)
    else:
        print("\nFailed to generate structured summary.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
