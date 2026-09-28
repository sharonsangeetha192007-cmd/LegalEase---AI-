from legal_ease.sanitization import sanitize_text


def test_sanitize_text_normalizes_typography():
    text = "Hello\u2019s  world\r\n\r\n\r\nNext\u2014section\u2026"
    assert sanitize_text(text) == "Hello's  world\n\n\nNext-section..."


def test_sanitize_text_rejects_non_string():
    import pytest

    with pytest.raises(TypeError):
        sanitize_text(None)
