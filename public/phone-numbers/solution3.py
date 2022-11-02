#!/usr/bin/env python
"""Usage: solution3.py numbers_file words_file"""
import sys
from typing import Dict, List, Set

NUMBER_TO_LETTERS = {
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

LETTER_TO_NUMBER = {
    letter: str(number)
    for (number, letters) in NUMBER_TO_LETTERS.items()
    for letter in letters
}


def main():
    numbers_file, words_file = sys.argv[1:]
    word_map = generate_word_map(words_file)

    with open(numbers_file) as numbers:
        for number in numbers:
            print_encodings(number.strip(), word_map)


def print_encodings(phone_number: str, word_map: Dict[str, Set[str]]) -> None:
    """Find all possible encodings for the given phone number and word list.

    Args:
        phone_number: A standardized phone number to find encodings for.
        word_map: A mapping from phone numbers to original words that could
            make them.

    Returns:
        A list of encodings, which takes the form of individual words from the
        dictionary, or a single digit, separated by a single space.
    """

    digits = standardize_phone_number(phone_number)
    if not digits:
        return

    def subsections(start: int) -> List[str]:
        """For k in the interval (start, len(phone_number)), gives all slices:
        phonenumber[start: k]
        """
        word = digits[start:]
        return [word[: end + 1] for end in range(len(word))]

    def find_encodings(
        sections: List[str], start: int = 0, last_was_digit: bool = False
    ) -> None:
        """Print all possible encodings of the slice: phone_number[start:].

        Args:
            sections: The original words (or numbers) that would be a valid encoding
                so far for the slice phone_number[: start]
            start: The index from which to search for potential encodings in
                phone_number.
            last_was_digit: An optional (redundant) parameter which is true iff
                the last section was a digit.
        """
        if start >= len(digits):
            print(f'{phone_number}: {" ".join(sections)}')
            return

        next_sections = list(
            filter(lambda section: section in word_map, subsections(start))
        )
        for section in next_sections:
            for original_word in word_map[section]:
                find_encodings(sections + [original_word], start + len(section))

        if not next_sections and not last_was_digit:
            find_encodings(sections + [digits[start]], start + 1, True)

    find_encodings([])


def generate_word_map(words_file: str) -> Dict[str, Set[str]]:
    """Generates a mapping from phone numbers to all original words that could
    have made that phone number.

    Args:
        words_file: A valid path to a words_file.
    """
    with open(words_file) as word_list:
        original_words = [word.strip() for word in word_list.readlines()]

    result: Dict[str, Set[str]] = {}
    for word in original_words:
        phone_number = word_to_phone_number(word)
        result.setdefault(phone_number, set()).add(word)

    return result


def word_to_phone_number(word: str) -> str:
    """Converts a word to its corresponding phone number."""
    letters = filter(lambda letter: letter.isalpha(), word.lower())
    return "".join(map(lambda letter: LETTER_TO_NUMBER[letter], letters))


def standardize_phone_number(phone_number: str) -> str:
    """Removes all non-numeric characters from a phone number."""
    return "".join(list(filter(lambda digit: digit.isnumeric(), phone_number)))


if __name__ == "__main__":
    main()
