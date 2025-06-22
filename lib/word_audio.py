import os
import requests
from dotenv import load_dotenv
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

AUDIO_URL_TEMPLATE = os.getenv("AUDIO_URL")
OUTPUT_DIR = "output/word_audio"


def download_all_audio(words_to_process, max_workers=10):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_word = {
            executor.submit(get_word_audio, expression, reading): expression
            for expression, reading in words_to_process
        }
        for future in concurrent.futures.as_completed(future_to_word):
            future.result()


def get_word_audio(expression, reading):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    filepath = os.path.join(OUTPUT_DIR, f"proper_nouns_{expression}.mp3")

    if os.path.exists(filepath):
        return

    retry_strategy = Retry(
        total=5,
        status_forcelist=[400, 429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    url = AUDIO_URL_TEMPLATE.replace(
        "{term}", expression).replace("{reading}", reading)

    print(f"Requesting audio sources from: {url}")
    response = session.get(url)
    response.raise_for_status()
    data = response.json()

    audio_source_url = None
    for source in data["audioSources"]:
        source_name = source.get("name", "")
        if "Only Reading" not in source_name and "Only Expression" not in source_name:
            audio_source_url = source["url"]
            break

    print(f"Downloading audio from: {audio_source_url}")

    audio_response = session.get(audio_source_url)
    audio_response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(audio_response.content)
    print(f"Saved audio for '{expression}' to '{filepath}'")
