---
layout: ../../layouts/PostLayout.astro
title: "Competing with Giants"
subtitle: "And getting humbled"
date: "2022-11-02"
---

Yesterday, I was reading through a [HackerNews post](https://news.ycombinator.com/item?id=33413124),
asking which pieces of software were _mindblowing_ upon first sight.

Among some of the usual suspects, I came across a comment by user `nl`,
describing a [simple spell-checker](http://norvig.com/spell-correct.html)
that Peter Norvig wrote on a plane ride, as an explanation to some friends on
how spell-checkers work.

For those who might not have heard of Peter Norvig, he's a giant in the field
of AI, and is currently Director of Research at Google. Computer science
students may recognize his amazing textbook-
[_Artifical Intelligence: A Modern Approach_](http://aima.cs.berkeley.edu/)
(the one with chess pieces on the front).

Norvig's spell-checker is a gorgeous thing. It's refined,
readable, and useful, and so fits my criteria for beauty in software. I'd
recommend reading the [source](http://norvig.com/spell-correct.html)
and equally wonderful explanations below it, if you're interested.

But this isn't meant to be a fanboy post; instead, this is about me, flexing
in the shadow of giants before being appropriately humbled.

## The Test

[Another post](http://norvig.com/java-lisp.html) on Norvig's site describes
some papers which compare programming languages for development time and
performance on a sample task.

Besides the results of the papers, the cool part was that Norvig included his
own solution (in Lisp), as well as how long it took him to complete the task!

- You can read the [original test instructions here.](https://flownet.com/ron/papers/lisp-java/instructions.html)
- The test inputs, expected results, and results of the study [can be found here.](https://flownet.com/ron/papers/lisp-java/)

And so I set out to test my mettle, in attempting to write a python solution in
less time than the 2 hours it took Peter Norvig (1.5 hours writing, 0.5 hours
documenting and bugfixing).

<!---
For those averse to reading the original instructions, the problem is essentially:

- Given:

  - a file containing (noisy) phone numbers
  - a file containing a (noisy) set of words (corpus)
  - a mapping from numbers to sets of letters

- Print, for each phone number, all possible encodings of words in the corpus
  that it might result from.
- Valid encodings take the form of **sections** separated by single spaces,
  where each section can be either:
  - **a word** from the original corpus
  - at max one consecutive **digit** if no word could be encoded for that section.
- The code must be documented as you would, professionally.
  -->

## My Timeline

- +0:00 - Begin Reading problem
- +0:05 - Half read problem, start writing solution
- +1:20 - Finished solution, count chickens, begin writing documentation.
- +1:50 - Finish documentation. Test on partial datasets, celebrate! Take break.
- +2:00 - Decide to try solution on full dataset. The horror. Begin rewriting.
- +3:15 - Finish and compare final solution to Norvig

At about +1:00 I was over the moon, thinking I'd finished much before any of
the other programmers in the study. Then I read the problem statement more
closely and realised I had made some wrong assumptions about how the output was
meant to be formatted.

Then at +1:20, finishing my first solution, I had pretty much the same feeling.
I ran the program on the smaller, test dataset which was provided, and when the
outputs matched, fist-pumped and began writing some documentation.

At +2:00 when it finally dawned upon me to test my solution on the full dataset,
I was stunned. Despite being correct, my program was horribly inefficient:

```zsh
command time -l python3 solution1.py numbers.txt words.txt
236.60 real       235.65 user         0.94 sys
            49217536  maximum resident set size
                   0  average shared memory size
                   0  average unshared data size
                   0  average unshared stack size
               81537  page reclaims
                   0  page faults
                   0  swaps
                   0  block input operations
                   0  block output operations
                   0  messages sent
                   0  messages received
                  10  signals received
                  25  voluntary context switches
                 274  involuntary context switches
       4367111360040  instructions retired
        747507413225  cycles elapsed
            24413312  peak memory footprint
```

For reference as to [how bad that is](https://flownet.com/ron/papers/lisp-java/raw-results.html),
this time of **237 seconds** is **3x worse** than the worst time in the study,
and **12x worse** than the best time.
By itself that might not be too bad- lisp can be much faster than python. Sure.
But then again, I'm running this on an M1 mac in 2022 while these results are
from 2000 running on god knows what.

When I ran Peter Norvig's solution on the dataset...

```zsh
❯ command time -l sbcl --script norvig.lsp > out
        0.09 real         0.06 user         0.02 sys
            61292544  maximum resident set size
                   0  average shared memory size
                   0  average unshared data size
                   0  average unshared stack size
                4776  page reclaims
                   0  page faults
                   0  swaps
                   0  block input operations
                   0  block output operations
                   0  messages sent
                   0  messages received
                  59  signals received
                   0  voluntary context switches
                  17  involuntary context switches
           587319952  instructions retired
           181442127  cycles elapsed
            60670976  peak memory footprint
```

0.09 seconds, or 2629x faster than my python solution! This is probably a better
benchmark for the best times from back in 2000.

So let's see why my solution performs so poorly!

## Original Solution 🤢

You can find my original solution [here](/phone-numbers/solution1.py).
See how many design flaws you can find, then we'll go over potential fixes.

### Design Flaws

#### 1. Unnecessary repeated file IO

The most obvious sin is re-opening and reading the word dictionary for
_every single phone number!_ I immediately wrote a `solution2.py` afterwards,
which just loads the dictionary once at the very beginning of the program.
The results of this were fairly expected, shaving off 80 seconds:

```zsh
❯ command time -l ./solution2.py input.txt dictionary.txt
 156.88 real       156.19 user         0.30 sys
 ...
```

#### 2. Reading every word in the dictionary for each potential encoded section.

Probably the most egregious flaw though, is in `find_encodings`:

```python
def find_encodings(
    phone_number: str, words: List[str], last_was_digit: bool = False
) -> List[str]:
  ...
  # Get a list of all the words that could be a valid next word.
  next_words = list(
      filter(lambda word: can_encode(phone_number[: len(word)], word), words)
  )
  ...
```

To generate `next_words`, we are actually checking _every single word_ in the
dictionary for _every phone number_. Without any proof, I'm going to claim that
this makes `find_encodings` O(really really bad).

Of course, had I read this line from the original problem, I could have saved
myself some time:

> Your program must be run time efficient in so far that it analyzes only
> a very small fraction of all dictionary entries in each word appending
> step.

Improving this shortcoming is heavily linked to the next step.

#### 3. Awkward choice of storage for the original words dictionary

Originally, to store the corpus, I built a dictionary which mapped standardized
words to their original counterparts. This is an awkward idea, because now,
determining if a word would be a valid encoding for a section of a phone number
requires a conversion process from one to the other. We have the potential
to perform this same conversion multiple times, unecessarily, when it could be
performed only once at the very start of the program.

#### 4. `find_encodings` only taking in the standardized list of words.

This forces an awkward step after all the encodings are found, where we must find
which sections can be mapped back to their original words.

Instead, we should pass in the entire dictionary which maps standardized words
to their original forms, and then encode the original word for a section instead
of the standardized form.

#### 5. `find_encodings` Returning a Result

We don't need to do anything additional to the encodings once we find them, so
`find_encodings` can just print the encodings as soon as they're found,
simplifying the internal logic.

And probably many more!

## Improved Solution

For my second attempt, I decided it would be much nicer to store the original
dictionary as a mapping from encoded phone numbers to a set of their potential
original words within the dictionary.

This gave the following solution (also available [here](/phone-numbers/solution3.py)):

```python
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
```

### Key improvements

- Now we're only checking at max all possible subsections of the phone number,
  rather than multiplying that by every word in the original dictionary.
- Adding the `sections` parameter to the `find_encodings` closure made the body much
  nicer, and was an idea I got from the section on tail-recursive calls in the
  beginning of SICP. I also wouldn't have thought to use the closure to hide
  the `start` and `last_was_digit` parameters without that book.
- By passing the entire mapping from `digits->set<original_word>`, we can add
  the original word to `sections` as opposed to the standardized form, avoiding
  an awkward reconversion process later.
- I know that `last_was_digit` is technically redundant, but its prettier to
  include it this way then check if `sections` is empty.

Also without further ado, the new runtime was **0.265 seconds** 🎉 and used around
38MB of memory.

## Comparing to Norvig's Solution

I was incredibly happy to find that I converged to the same solution as Norvig,
even though it took me an extra hour and a bit (and I didn't document anywhere
near as much as he did). The main differences are:

- He encoded the original words as digits representing the converted phone
  numbers rather than strings of the same thing.
- I'm calculating all subsections of the phonenumber a little more eagerly,
  while he's unrolling them in a loop.
- His solution contains so few lines of code that it's kind of bizarre.
- His solution uses 60MB compared to my 38MB, but as far as I can tell, his
  should actually be using less than mine and I'm thinking this is something to
  do with Python vs lisp?

Also if anybody is skeptical that I just read his solution ahead of time
for my second attempt and converted it to python, I will say that as somebody
quite unpracticed with lisp, it took me more time to read/lookup/understand his
solution than to write mine.

## Conclusion

This turned out to be alot of fun in the end. I hadn't had the chance to write
this sort of program (non-trivial and well defined) in a long time, so it was
nice to exercise that part of my brain.

As for how my experience relates to the point of the original studies- I was
able to produce a python solution in comparable time to the lisp participants,
and which ran within (probably) the same efficiency range. It's hard to know
this for sure without running the unavailable code from the other participants on my machine.
