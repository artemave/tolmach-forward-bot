from bot.text_extraction import extract_command_target, extract_text
from tests.conftest import make_message


def test_returns_none_when_message_is_none() -> None:
    assert extract_text(None) is None


def test_returns_text_when_present() -> None:
    assert extract_text(make_message(text="Hello")) == "Hello"


def test_returns_caption_when_there_is_no_text() -> None:
    assert extract_text(make_message(text=None, caption="A caption")) == "A caption"


def test_returns_none_without_text_or_caption() -> None:
    assert extract_text(make_message(text=None, caption=None)) is None


# --------------------------------------------------------------------------- #
# extract_command_target — quote > reply_to fallback > None
# --------------------------------------------------------------------------- #
def test_command_target_returns_none_when_message_is_none() -> None:
    assert extract_command_target(None) is None


def test_command_target_prefers_the_quoted_selection() -> None:
    inner = make_message(text="original full translation")
    message = make_message(text="/explain", reply_to=inner, quote_text="word")
    assert extract_command_target(message) == "word"


def test_command_target_falls_back_to_replied_message_text_without_quote() -> None:
    inner = make_message(text="full translation")
    message = make_message(text="/explain", reply_to=inner)
    assert extract_command_target(message) == "full translation"


def test_command_target_treats_empty_quote_as_no_quote() -> None:
    inner = make_message(text="full translation")
    message = make_message(text="/explain", reply_to=inner, quote_text="")
    assert extract_command_target(message) == "full translation"


def test_command_target_returns_none_when_neither_quote_nor_reply() -> None:
    message = make_message(text="/explain")
    assert extract_command_target(message) is None
