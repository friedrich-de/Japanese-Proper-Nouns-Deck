import os
import dotenv
import openai
import concurrent.futures
from typing import List, Dict, Tuple

dotenv.load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "google/gemini-2.5-flash-preview"

client = openai.OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

OUTPUT_DIR = "output/explanations"


def get_explanation_prompt(expression: str, reading: str, noun_type: str) -> str:
    """Generate a prompt based on the type of proper noun"""

    if noun_type.lower() == "fam":  # Family name/personal name
        return f"""You are a Japanese language expert. Please provide a concise explanation (2-3 sentences) for the Japanese name "{expression}" (読み: {reading}).

Include:
- The meaning of the kanji characters or name components
- Any historical or cultural significance
- Common usage or notable associations

Respond in English, keeping it informative but brief."""

    elif noun_type.lower() == "loc":  # Location name
        return f"""You are a Japanese geography and culture expert. Please provide a concise explanation (2-3 sentences) for the Japanese place name "{expression}" (読み: {reading}).

Include:
- Where this place is located (prefecture, region, etc.)
- Its significance (historical, cultural, economic, or tourist importance)
- Any notable features or characteristics

Respond in English, keeping it informative but brief."""

    else:  # Default case
        return f"""You are a Japanese language expert. Please provide a concise explanation (2-3 sentences) for the Japanese proper noun "{expression}" (読み: {reading}).

Include relevant information about its meaning, significance, or usage context.

Respond in English, keeping it informative but brief."""


def generate_explanation(expression: str, reading: str, noun_type: str) -> str:
    prompt = get_explanation_prompt(expression, reading, noun_type)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    explanation = response.choices[0].message.content.strip()
    return explanation


def process_single_explanation(expression: str, reading: str, noun_type: str) -> Tuple[str, str]:
    explanation_path = os.path.join(OUTPUT_DIR, f"{expression}.txt")
    if os.path.exists(explanation_path):
        with open(explanation_path, "r", encoding="utf-8") as f:
            existing_explanation = f.read().strip()
        return expression, existing_explanation

    explanation = generate_explanation(expression, reading, noun_type)

    with open(explanation_path, "w", encoding="utf-8") as f:
        f.write(explanation)

    return expression, explanation


def generate_all_explanations(data: List[Dict], max_workers: int = 10) -> Dict[str, str]:
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    explanations = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_expr = {
            executor.submit(
                process_single_explanation,
                entry["Expression"],
                entry["Main_Reading"],
                entry["Main_Reading_Type"]
            ): entry["Expression"]
            for entry in data
        }

        completed = 0
        total = len(data)

        for future in concurrent.futures.as_completed(future_to_expr):
            expression, explanation = future.result()
            completed += 1
            explanations[expression] = explanation
            if completed % 500 == 0 or completed == total:
                print(
                    f"[{completed}/{total}] Generated explanation for '{expression}'")
