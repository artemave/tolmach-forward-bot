from bot.text_extraction import extract_text
from tests.conftest import make_message


def test_returns_none_when_message_is_none() -> None:
    assert extract_text(None) is None


def test_returns_text_when_present() -> None:
    assert extract_text(make_message(text="Hello")) == "Hello"


def test_returns_caption_when_there_is_no_text() -> None:
    assert extract_text(make_message(text=None, caption="A caption")) == "A caption"


def test_returns_none_without_text_or_caption() -> None:
    assert extract_text(make_message(text=None, caption=None)) is None
