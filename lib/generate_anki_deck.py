import os
import genanki
import html
import markdown
from typing import List, Dict
import sys

MODEL_ID = 1627393320
DECK_ID = 3059410111


def load_template_files():
    with open("fields/front.html", "r", encoding="utf-8") as f:
        front_template = f.read()

    with open("fields/back.html", "r", encoding="utf-8") as f:
        back_template = f.read()

    with open("fields/styling.css", "r", encoding="utf-8") as f:
        css_styling = f.read()

    return front_template, back_template, css_styling


def get_proper_nouns_model():
    """Create and return the proper nouns model with templates loaded from files"""
    front_template, back_template, css_styling = load_template_files()

    return genanki.Model(
        MODEL_ID,
        'Japanese Proper Nouns',
        fields=[
            {'name': 'Expression'},
            {'name': 'Main_Reading'},
            {'name': 'Main_Reading_Frequency'},
            {'name': 'Main_Reading_Type'},
            {'name': 'Explanation'},
            {'name': 'Other_Readings'},
            {'name': 'Other_Readings_Frequency'},
            {'name': 'Other_Readings_Types'},
            {'name': 'Word_Audio'},
            {'name': 'Picture'},
            {'name': 'Picture_Caption'},
        ],
        templates=[
            {
                'name': 'Recognition Card',
                'qfmt': front_template,
                'afmt': back_template,
            },
        ],
        css=css_styling
    )


def load_explanation(expression: str) -> str:
    explanation_path = os.path.join(
        "output", "explanations", f"{expression}.txt")
    with open(explanation_path, "r", encoding="utf-8") as f:
        explanation_text = f.read().strip()
        html_explanation = markdown.markdown(explanation_text)
        return html_explanation


def load_picture_caption(expression: str) -> str:
    caption_path = os.path.join(
        "output", "images", f"proper_nouns_{expression}_description.txt")
    with open(caption_path, "r", encoding="utf-8") as f:
        caption_text = f.read().strip()
        html_caption = markdown.markdown(caption_text)
        return html_caption


def get_media_files() -> List[str]:
    media_files = []

    images_dir = os.path.join("output", "images")
    for filename in os.listdir(images_dir):
        if filename.endswith('.jpg'):
            media_files.append(os.path.join(images_dir, filename))

    audio_dir = os.path.join("output", "word_audio")
    for filename in os.listdir(audio_dir):
        if filename.endswith('.mp3'):
            media_files.append(os.path.join(audio_dir, filename))

    return media_files


def create_note(entry: Dict, model: genanki.Model, due) -> genanki.Note:
    expression = entry["Expression"]

    explanation = load_explanation(expression)

    picture_caption = load_picture_caption(expression)

    other_readings = ""
    other_readings_frequency = ""
    other_readings_types = ""
    if entry["Other_Readings"]:
        other_readings = " / ".join(entry["Other_Readings"])
        other_readings_frequency = " / ".join(
            entry["Other_Readings_Frequency"])
        other_readings_types = " / ".join(
            entry["Other_Readings_Types"]) if entry["Other_Readings_Types"] else ""

    picture_html = ""
    image_filename = f"proper_nouns_{expression}.jpg"
    image_path = os.path.join("output", "images", image_filename)
    if os.path.exists(image_path):
        picture_html = f'<img src="{image_filename}">'
    else:
        sys.exit(f"Image file not found: {image_path}")

    audio_html = ""
    audio_filename = f"proper_nouns_{expression}.mp3"
    audio_path = os.path.join("output", "word_audio", audio_filename)
    if os.path.exists(audio_path):
        audio_html = f'[sound:{audio_filename}]'
    else:
        sys.exit(f"Audio file not found: {audio_path}")

    note = genanki.Note(
        model=model,
        fields=[
            html.escape(expression),
            html.escape(entry["Main_Reading"]),
            html.escape(entry["Main_Reading_Frequency"]),
            html.escape(entry["Main_Reading_Type"]),
            explanation,
            html.escape(other_readings),
            html.escape(other_readings_frequency),
            html.escape(other_readings_types),
            audio_html,
            picture_html,
            picture_caption,
        ],
        guid=genanki.guid_for(expression),
        due=due
    )

    return note


def generate_anki_deck(data: List[Dict], output_filename: str = "proper_nouns_deck_mk2.apkg") -> None:
    model = get_proper_nouns_model()

    deck = genanki.Deck(DECK_ID, 'Japanese Proper Nouns Deck Mk II')

    due = 0
    sorted_data = sorted(data, key=lambda x: x["Count"], reverse=True)
    for entry in sorted_data:
        due += 1
        note = create_note(entry, model, due)
        deck.add_note(note)

    media_files = get_media_files()

    package = genanki.Package(deck)
    package.media_files = media_files

    output_path = os.path.join("output", output_filename)
    os.makedirs("output", exist_ok=True)
    package.write_to_file(output_path)

    print(f"Generated Anki deck with {len(data)} notes")
    print(f"Included {len(media_files)} media files")
    print(f"Deck saved to: {output_path}")

    return data
