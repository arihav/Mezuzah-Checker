import json

from OCR import Letter


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

def save_letters_to_json(letters: list[Letter]):
    formatted_letters = [
        {to_camel_case(k): v for k, v in letter.to_dict().items()} for letter in letters
    ]
    with open('letters.json', "w", encoding="utf-8") as file:
        json.dump(formatted_letters, file, indent=4, ensure_ascii=False)
