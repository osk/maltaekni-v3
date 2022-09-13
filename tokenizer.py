# pylint: disable=missing-function-docstring
"""
> Some people, when confronted with a problem, think
> “I know, I'll use regular expressions.” Now they have two problems.
> — JWZ
"""

WORD = 1
NUMBER = 2
PUNCTUATION = 3
WHITESPACE = 4
ABBREVIATION = 5

CHARS_IN_WORD = "aábcdðeéfghiíjklmnoóprstuúvxyýþæöw-"
# CHARS_IN_WORD = "td"
CHARS_NUMBER = "1234567890"
CHARS_IN_PUNCTUATION = '_–—!"#$&()*+,./:;’“”?'
CHARS_IN_WHITESPACE = " \t\n"
KNOWN_ABBREVIATIONS = ["t.d.", "m.a.", "þ.á.m.", "þ.á m."]


class TokenizeOr:
    label = "or"

    def __init__(self, tokenizers):
        self.tokenizers = tokenizers

    def tokenize(self, input, depth=1):
        results = []
        for tokenizer in self.tokenizers:
            tokenized = tokenizer.tokenize(input, depth + 1)
            results.append((tokenized, tokenizer.priority))

        results_sorted = sorted(results, key=lambda result: result[1], reverse=True)

        # Find the item which matched, or None
        ok = next(
            (item for (item, priority) in results_sorted if item[1] is not None),
            None,
        )

        if depth > 900:
            return ok

        # If no match, return the first one (they should all be the same)
        if not ok:
            return results[0]

        return ok


class TokenizeChar:
    label = "char"

    def __init__(self, char, priority=0):
        self.char = char
        self.priority = priority

    def tokenize(self, input, depth=1):
        (stream, _) = input
        source = stream["source"]
        index = stream["index"]

        if not stream or index >= len(source):
            return (stream, None)

        next_letter = source[index]

        if self.char.lower() == next_letter.lower():
            return (
                {
                    "source": stream["source"],
                    "index": stream["index"] + 1,
                },
                [next_letter],
            )

        return (stream, None)


class TokenizeChars:
    def __init__(self, words, priority=0):
        self.words = words
        self.priority = priority

    def create(self):
        chars = [*self.words]

        tokenizers = []
        for char in chars:
            tokenizers.append(TokenizeChar(char))
        orTokenizer = TokenizeOr(tokenizers)

        return orTokenizer


class TokenizeZeroOrMore:
    def __init__(self, tokenizer, priority=0):
        self.tokenizer = tokenizer
        self.priority = priority

    def tokenize(self, input, depth=1):
        """
        Call the tokenizer
        Resulting stream advanced
        If value, try again, otherwise return (stream, value)
        """
        (stream, value) = input
        tokenized = self.tokenizer.tokenize(input, depth + 1)

        if not tokenized:
            return (stream, value)

        (result_stream, result_value) = tokenized

        print("zero depth", depth)

        # We got something from the tokenizer, continue
        if result_value:
            if depth > 900:
                return (stream, value + result_value)

            return self.tokenize((result_stream, value + result_value), depth + 1)

        return (stream, value)


class TokenizeOneOrMore:
    def __init__(self, tokenizer, priority=0):
        self.tokenizer = tokenizer
        self.priority = priority

    def tokenize(self, input, depth=1):
        """
        Must get a success on first try
        If so, call rest with ZeroOrMore
        If not, return fail
        """
        tokenized = self.tokenizer.tokenize(input, depth + 1)

        if not tokenized:
            return input

        (result_stream, result_value) = tokenized

        if result_value:
            zero_or_more = TokenizeZeroOrMore(self.tokenizer)
            return zero_or_more.tokenize((result_stream, result_value), 1)
        else:
            return (result_stream, None)


class TokenizeString:
    label = "string"

    def __init__(self, words, type, priority=0):
        chars_tokenizer = TokenizeChars(words).create()
        self.tokenizer = TokenizeOneOrMore(chars_tokenizer)
        self.type = type
        self.priority = priority

    def tokenize(self, input, depth=1):
        (stream, value) = self.tokenizer.tokenize(input, depth + 1)

        # Is there a value? Return it with given type
        if value:
            if isinstance(value, str):
                return (stream, value)
            else:
                return (stream, [("".join(value), self.type)])
        else:
            return (stream, None)


class TokenizeKnownString:
    label = "known_string"

    def __init__(self, string, priority=0):
        self.string = string
        self.priority = priority

    def tokenize(self, input, depth=1):
        (stream, _) = input
        source = stream["source"]
        index = stream["index"]

        if not stream or index >= len(source):
            return (stream, None)

        str_len = len(self.string)

        next_letters = source[index : index + str_len]

        if self.string.lower() == next_letters.lower():
            return (
                {
                    "source": stream["source"],
                    "index": stream["index"] + str_len,
                },
                [next_letters],
            )

        return (stream, None)


class TokenizeKnownStrings:
    label = "known_strings"

    def __init__(self, strings, type, priority=0):
        tokenizers = []
        for string in strings:
            tokenizers.append(TokenizeKnownString(string))

        self.tokenizer = TokenizeOr(tokenizers)
        self.type = type
        self.priority = priority

    def tokenize(self, input, depth=1):
        (stream, value) = self.tokenizer.tokenize(input, depth + 1)

        # Is there a value? Return it with given type
        if value:
            return (stream, [(value[0], self.type)])
        else:
            return (stream, None)


def tokenize(i: str, keep_whitespace=True):
    # input into tokenizers are on the form
    # (stream: {source: string, index: number}, value: list((string, type)))
    input = ({"source": i, "index": 0}, [])

    word_tokenizer = TokenizeString(CHARS_IN_WORD, WORD)
    number_tokenizer = TokenizeString(CHARS_NUMBER, NUMBER)
    whitespace_tokenizer = TokenizeString(CHARS_IN_WHITESPACE, WHITESPACE)
    punctuation_tokenizer = TokenizeString(CHARS_IN_PUNCTUATION, PUNCTUATION)
    known_abbreviations_tokenizer = TokenizeKnownStrings(
        KNOWN_ABBREVIATIONS, ABBREVIATION, 99
    )

    combined_tokenizer = TokenizeZeroOrMore(
        TokenizeOr(
            [
                whitespace_tokenizer,
                number_tokenizer,
                word_tokenizer,
                punctuation_tokenizer,
                known_abbreviations_tokenizer,
            ]
        )
    )

    (_, value) = combined_tokenizer.tokenize(input)

    if not keep_whitespace:
        return [token for token in value if token[1] != WHITESPACE]

    return value


if __name__ == "__main__":
    p_and_p = ""
    with open("./data/songlog.txt", "rb") as input_file:
        p_and_p = input_file.read().decode("utf8")
        toks = tokenize(p_and_p)
        print(toks)
