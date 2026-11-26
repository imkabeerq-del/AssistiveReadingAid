# sentence_splitter.py

import re


def split_sentences(text):

    if not text or not text.strip():
        return []

    protected = {}
    counter = 0

    patterns = [

        # Titles
        r"\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr)\.",

        # Common abbreviations
        r"\b(?:e\.g|i\.e|etc)\.",

        # Academic abbreviations
        r"\b(?:Ph\.D|M\.Sc|B\.Sc)\.",

        # Initials
        r"(?:[A-Z]\.){2,}",

        # Acronyms
        r"(?:[A-Z]{2,}\.)+",

        # Decimal numbers
        r"\d+\.\d+"

    ]

    # ----------------------------------
    # Protect abbreviations and decimals
    # ----------------------------------

    for pattern in patterns:

        matches = list(
            re.finditer(pattern, text)
        )

        for match in matches:

            token = f"__PROTECTED_{counter}__"

            protected[token] = (
                match.group()
            )

            text = text.replace(
                match.group(),
                token,
                1
            )

            counter += 1

    # ----------------------------------
    # Protect apostrophes
    # ----------------------------------

    text = re.sub(
        r"([A-Za-z])'([A-Za-z])",
        r"\1__APOS__\2",
        text
    )

    text = re.sub(
        r"([A-Za-z])’([A-Za-z])",
        r"\1__SMART_APOS__\2",
        text
    )

    # ----------------------------------
    # Protect escaped quotes
    # ----------------------------------

    text = text.replace(
        r"\"",
        "__DQUOTE__"
    )

    text = text.replace(
        r"\'",
        "__SQUOTE__"
    )

    # ----------------------------------
    # Insert sentence boundaries
    # Handles:
    # Hello.World
    # "Hello."World
    # (Text.)Next
    # Really?Yes
    # ----------------------------------

    text = re.sub(
        r'([.!?]["“”\'‘’)\]}]*)(?=[A-Za-z])',
        r'\1<SPLIT>',
        text
    )

    # ----------------------------------
    # Split
    # ----------------------------------

    parts = re.split(
        r'<SPLIT>|(?<=[.!?])\s+',
        text
    )

    sentences = []

    for sentence in parts:

        for token, original in protected.items():

            sentence = sentence.replace(
                token,
                original
            )

        sentence = sentence.replace(
            "__APOS__",
            "'"
        )

        sentence = sentence.replace(
            "__SMART_APOS__",
            "’"
        )

        sentence = sentence.replace(
            "__DQUOTE__",
            '"'
        )

        sentence = sentence.replace(
            "__SQUOTE__",
            "'"
        )

        sentence = sentence.strip()

        if sentence:

            sentences.append(
                sentence
            )

    return sentences


if __name__ == "__main__":

    sample = """
    Dr. Sharma said,"Reading is important."The students listened.
    The score was 3.14.Next sentence.
    Don't stop.It's working.
    """

    print(
        split_sentences(sample)
    )