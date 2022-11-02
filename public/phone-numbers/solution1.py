#!/usr/bin/env python
"""Usage: solution1.py numbers_file words_file"""
import sys
from itertools import chain
from pathlib import Path
from typing import Dict, List

NUMBER_MAP = {
    0: "e",
    1: "jnq",
    2: "rwx",
    3: "dsy",
    4: "ft",
    5: "am",
    6: "civ",
    7: "bku",
    8: "lop",
    9: "ghz",
}

LETTER_MAP = {
    letter: number for (number, letters) in NUMBER_MAP.items() for letter in letters
}


def main():
    numbers_file, words_file = sys.argv[1:]
    with open(numbers_file) as numbers:
        for number in numbers:
            print_encodings(number.strip(), Path(words_file))


def print_encodings(phone_number: str, word_dict: Path) -> None:
    """Prints out a list of all possible encodings for the given phone number.

    Encodings of phone numbers can consist of a single word or of multiple
    words separated by spaces. The encodings are built word by word from
    left to right. If and only if at a particular point no word at all from
    the dictionary can be inserted, a single digit from the phone number can
    be copied to the encoding instead. Two subsequent digits are never
    allowed, though.

    Args:
        phone_number: A phone number which is an arbitrary(!) string of dashes
            - , slashes / and digits
        word_dict: The path to a dictionary containing a list of words to use
            for potential sections of the encoding.
    """
    with open(word_dict) as word_list:
        original_words = [word.strip() for word in word_list.readlines()]
    word_map = {standardize_word(word): word for word in original_words}

    encodings = find_encodings(
        standardize_phone_number(phone_number), list(word_map.keys())
    )
    for encoding in encodings:
        print(f"{phone_number}: {convert_back(encoding, word_map)}")


def standardize_word(word: str) -> str:
    """Removes all non-alphabet characters from a word and converts it to lower
    case.
    """
    return "".join(list(filter(lambda letter: letter.isalpha(), word.lower())))


def standardize_phone_number(phone_number: str) -> str:
    """Removes all non-numeric characters from a phone number."""
    return "".join(list(filter(lambda digit: digit.isnumeric(), phone_number)))


def find_encodings(
    phone_number: str, words: List[str], last_was_digit: bool = False
) -> List[str]:
    """Find all possible encodings for the given phone number and word list.

    Args:
        phone_number: A standardized phone number to find encodings for.
        words: A standardized list of words to make sections of the encoding.
        last_was_digit: An optional argument which shouldn't be set manually.
            Represents if the last recursive call ended by encoding a digit.

    Returns:
        A list of encodings, which takes the form of individual words from the list
        (or a single digit), separated by a single space.
    """

    if not len(phone_number):
        return []

    # Get a list of all the words that could be a valid next word.
    next_words = list(
        filter(lambda word: can_encode(phone_number[: len(word)], word), words)
    )

    def remaining_encodings(last_section: str) -> List[str]:
        remaining = phone_number[len(last_section) :]
        if not len(remaining):
            return [last_section]

        return [
            f"{last_section} {encoding}"
            for encoding in find_encodings(
                remaining, words, last_was_digit=last_section.isdigit()
            )
        ]

    if not len(next_words):
        return [] if last_was_digit else remaining_encodings(phone_number[0])

    # awkward flat map
    encodings = (remaining_encodings(word) for word in next_words)
    return list(chain(*encodings))


def can_encode(phone_number: str, word: str) -> bool:
    """Returns true iff the given word would be a valid encoding for the supplied
    phone number."""
    if len(phone_number) != len(word):
        return False

    for letter, number in zip(word, phone_number):
        if str(LETTER_MAP[letter]) != number:
            return False

    return True


def convert_back(encoding: str, word_map: Dict[str, str]) -> str:
    """Converts the sections within an encoding back to their original forms in
    the dictionary.

    Args:
        encoding: A encoding consisting of multiple standardized_words or single
            digits, separated by whitespace.
        word_map: A map from standardized words to their originals.

    Returns:
        The encoding using the original word list where possible.
    """
    sections = encoding.split()

    def revert(section):
        return word_map.get(section, section)

    return " ".join(map(revert, sections))


if __name__ == "__main__":
    main()
