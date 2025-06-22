from lib.parse_input import read_proper_nouns
from lib.word_audio import download_all_audio
from lib.get_images import download_all_images
from lib.get_explanations import generate_all_explanations
from lib.generate_anki_deck import generate_anki_deck

# Final fields: Expression,
# Main_Reading, Main_Reading_Frequency, Main_Reading_Type,
# Explanation,
# Other_Readings, Other_Readings_Frequency, Other_Readings_Types,
# Word_Audio
# Picture, Picture_Caption

if __name__ == "__main__":
    data = read_proper_nouns()
    print("Finished reading proper nouns.")
    expression_reading_pairs = [
        (entry["Expression"], entry["Main_Reading"]) for entry in data]

    download_all_audio(expression_reading_pairs)
    print("Finished downloading audio files.")
    download_all_images(expression_reading_pairs)
    print("Finished downloading images.")
    generate_all_explanations(data)
    print("Finished generating explanations.")
    generate_anki_deck(data)
    print("Finished generating Anki deck.")
