from duckduckgo_search import DDGS
import os
import dotenv
import requests
from PIL import Image
import io
import concurrent.futures
import time
from browserforge.headers import HeaderGenerator

dotenv.load_dotenv()

OUTPUT_DIR = "output/images"
PROXY = os.getenv("DDGS_PROXY")


def download_all_images(expression_reading_pairs, max_workers=500):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_expr = {executor.submit(
            process_single_expression, expr, reading): expr for expr, reading in expression_reading_pairs}

        completed = 0
        total = len(expression_reading_pairs)
        for future in concurrent.futures.as_completed(future_to_expr):
            expr = future_to_expr[future]
            future.result()
            completed += 1
            if completed % 500 == 0 or completed == total:
                print(f"[{completed}/{total}] Completed processing '{expr}'")


def get_random_headers():
    headers = HeaderGenerator()
    return headers.generate()


def process_single_expression(expression, reading):
    max_retries = 10
    retry_count = 0

    while retry_count <= max_retries:
        try:
            headers = get_random_headers()
            with DDGS(headers=headers, proxy=PROXY, timeout=60) as ddgs:
                get_image(expression, reading, ddgs)
                return expression
        except Exception as e:
            if not "202" in str(e) and not "403" in str(e):
                print(f"Error processing '{expression}': {e}")
            retry_count += 1
            time.sleep(1)

    return expression


def get_image(expression, reading, ddgs: DDGS):
    image_path = os.path.join(OUTPUT_DIR, f"proper_nouns_{expression}.jpg")
    description_path = os.path.join(
        OUTPUT_DIR, f"proper_nouns_{expression}_description.txt")

    if os.path.exists(image_path):
        return

    results = ddgs.images(
        keywords=f"image {expression} {reading}",
        region="jp-jp",
        safesearch="moderate",
        max_results=10
    )

    selected_image = None
    for result in results:
        if expression in result['title']:
            selected_image = result
            break

    if not selected_image:
        selected_image = results[0]

    thumbnail_url = selected_image['thumbnail']
    title = selected_image['title']

    response = requests.get(thumbnail_url, timeout=10)
    response.raise_for_status()

    img_data = io.BytesIO(response.content)
    with Image.open(img_data) as img:
        img.thumbnail((500, 500))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(image_path, "jpeg")

    print(f"Saved image for '{expression}' to '{image_path}'")

    with open(description_path, "w", encoding="utf-8") as f:
        f.write(title)
    print(f"Saved description for '{expression}' to '{description_path}'")
