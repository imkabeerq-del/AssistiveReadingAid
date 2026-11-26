from sentence_splitter import split_sentences


def test_no_space_after_period():

    assert split_sentences(
        "Hello.World."
    ) == [
        "Hello.",
        "World."
    ]


def test_title():

    assert split_sentences(
        "Dr. Sharma arrived.Next sentence."
    ) == [
        "Dr. Sharma arrived.",
        "Next sentence."
    ]


def test_decimal():

    assert split_sentences(
        "The value is 3.14.Next sentence."
    ) == [
        "The value is 3.14.",
        "Next sentence."
    ]


def test_apostrophe():

    assert split_sentences(
        "Don't stop.It's working."
    ) == [
        "Don't stop.",
        "It's working."
    ]


def test_smart_apostrophe():

    assert split_sentences(
        "Don’t stop.It’s working."
    ) == [
        "Don’t stop.",
        "It’s working."
    ]


def test_quote():

    assert split_sentences(
        '"Hello."World.'
    ) == [
        '"Hello."',
        "World."
    ]


def test_smart_quote():

    assert split_sentences(
        '“Hello.”World.'
    ) == [
        '“Hello.”',
        "World."
    ]


def test_nested_quote():

    assert split_sentences(
        'She said,“He replied, \'Yes.\'”Then left.'
    ) == [
        'She said,“He replied, \'Yes.\'”',
        "Then left."
    ]


def test_parentheses():

    assert split_sentences(
        "(Example sentence.)Next sentence."
    ) == [
        "(Example sentence.)",
        "Next sentence."
    ]


def test_exclamation():

    assert split_sentences(
        "Amazing!Wonderful!"
    ) == [
        "Amazing!",
        "Wonderful!"
    ]