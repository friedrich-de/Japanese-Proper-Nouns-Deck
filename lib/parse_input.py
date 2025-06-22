import re


def read_proper_nouns():
    proper_noun_data = []

    with open("Proper_Nouns.txt", "r") as file:
        proper_nouns = file.read().splitlines()

    for proper_noun in proper_nouns:
        expression, readings, count = proper_noun.split("\t")
        print(
            f"Expression: {expression}, Readings: {readings}, Count: {count}")
        reading_pattern = r"\((\w+)\)(.*?)\((\d+%)\)"
        matches = re.findall(reading_pattern, readings)
        main_reading = ""
        main_reading_frequency = ""
        main_reading_type = ""
        other_readings = []
        other_readings_frequency = []
        other_readings_types = []

        for index, (type, reading, frequency) in enumerate(matches):
            if index == 0:
                main_reading = reading
                main_reading_frequency = frequency
                main_reading_type = type
            else:
                other_readings.append(reading)
                other_readings_frequency.append(frequency)
                other_readings_types.append(type)

        proper_noun_data.append({
            "Expression": expression,
            "Main_Reading": main_reading,
            "Main_Reading_Frequency": main_reading_frequency,
            "Main_Reading_Type": main_reading_type,
            "Explanation": "",
            "Other_Readings": other_readings,
            "Other_Readings_Frequency": other_readings_frequency,
            "Other_Readings_Types": other_readings_types,
            "Word_Audio": "",
            "Sentence_Audio": "",
            "Picture": "",
            "Picture_Caption": "",
            "Count": int(count)
        })

    return proper_noun_data
