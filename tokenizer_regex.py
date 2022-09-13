import re
from string import punctuation


WORD = 1
NUMBER = 2
PUNCTUATION = 3
WHITESPACE = 4
ABBREVIATION = 5

CHARS_IN_PUNCTUATION = "_–—!\"#$&()*+,./:;’“”?„-'´‛‘…­"
KNOWN_ABBREVIATIONS = ["t.d.", "m.a.", "þ.á.m.", "þ.á m."]
CHARS_IN_WORD = "aábcdðeéfghiíjklmnoóprstuúvxyýþæöwzùåäqêà"


def matches(i: str, r: re.Pattern):
    matches = re.match(r, i)

    if matches:
        return matches.group(0)
    return None


def tokenize(i: str, keep_whitespace=True):
    whitespace_regex = re.compile(r"^\s+")
    word_regex = re.compile(r"^([" + CHARS_IN_WORD + "]-?)+", re.IGNORECASE)
    number_regex = re.compile(r"^[0-9]+")
    punctuation_regex = re.compile(r"^[" + re.escape(CHARS_IN_PUNCTUATION) + "]+")
    abbreviation_regex = re.compile(
        "^(" + "|".join(map(re.escape, KNOWN_ABBREVIATIONS)) + ")"
    )

    ordered_matchers = [
        (whitespace_regex, WHITESPACE),
        (abbreviation_regex, ABBREVIATION),
        (punctuation_regex, PUNCTUATION),
        (number_regex, NUMBER),
        (word_regex, WORD),
    ]

    tokenized = []

    iterations = 0
    matched = True
    while matched:
        iterations = iterations + 1

        # Assume we won't match, fall through and then exit while
        matched = False
        for (matcher, matcher_type) in ordered_matchers:
            match = matches(i, matcher)
            if match:
                tokenized.append((match, matcher_type))
                i = i[len(match) :]
                # Something matched! We live to iterate another day
                matched = True
                # We don't want to match more than once per iteration
                break

    if len(i) > 10:
        print(i[0:10])

    if not keep_whitespace:
        return [token for token in tokenized if token[1] != WHITESPACE]

    return tokenized
