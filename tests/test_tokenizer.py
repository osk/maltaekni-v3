# pylint: disable=missing-module-docstring,missing-function-docstring

from tokenizer import ABBREVIATION, NUMBER, PUNCTUATION, WHITESPACE, WORD, tokenize


def test_tokenize_empty():
    assert tokenize("") == []


def test_tokenize_single_whitespace():
    assert tokenize(" ") == [(" ", WHITESPACE)]


def test_tokenize_multiple_whitespace():
    assert tokenize(" \t ") == [(" \t ", WHITESPACE)]


def test_tokenize_word():
    assert tokenize("forrit") == [("forrit", WORD)]


def test_tokenize_word_and_whitespace():
    assert tokenize("forrit ") == [("forrit", WORD), (" ", WHITESPACE)]


def test_tokenize_two_words():
    assert tokenize("forrit keyrir") == [
        ("forrit", WORD),
        (" ", WHITESPACE),
        ("keyrir", WORD),
    ]


def test_tokenize_long_string():
    assert tokenize("þetta    er \n forrit sem keyrir") == [
        ("þetta", WORD),
        ("    ", WHITESPACE),
        ("er", WORD),
        (" \n ", WHITESPACE),
        ("forrit", WORD),
        (" ", WHITESPACE),
        ("sem", WORD),
        (" ", WHITESPACE),
        ("keyrir", WORD),
    ]


def test_tokenize_punctuation():
    assert tokenize("!") == [("!", PUNCTUATION)]


def test_tokenize_number():
    assert tokenize("123") == [("123", NUMBER)]


def test_tokenize_abbreviation():
    assert tokenize("t.d.") == [("t.d.", ABBREVIATION)]


def test_tokenize_multiple_abbreviations():
    tokens = tokenize("m.a. t.d. þ.á.m.")
    print(tokens)
    assert tokens == [
        ("m.a.", ABBREVIATION),
        (" ", WHITESPACE),
        ("t.d.", ABBREVIATION),
        (" ", WHITESPACE),
        ("þ.á.m.", ABBREVIATION),
    ]


def test_tokenize_uppercase():
    assert tokenize("FoRriT") == [("FoRriT", WORD)]


def test_given_text():
    input = "Jón hefur m.a. starfað t.d. sem gítar- og píanókennari, þ.á m. hjá Ice-Music, frá árinu 1999."
    output = [
        "Jón",
        "hefur",
        "m.a.",
        "starfað",
        "t.d.",
        "sem",
        "gítar-",
        "og",
        "píanókennari",
        ",",
        "þ.á m.",
        "hjá",
        "Ice-Music",
        ",",
        "frá",
        "árinu",
        "1999",
        ".",
    ]
    tokens = tokenize(input, keep_whitespace=False)
    just_values = [token[0] for token in tokens]
    assert just_values == output


def test_tokenize_abbreviation_and_whitespace():
    tokens = tokenize(" t.d.")
    assert tokens == [
        (" ", WHITESPACE),
        ("t.d.", ABBREVIATION),
    ]
