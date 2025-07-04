from document_processor import extract_text

def test_txt_extraction():
    text, error = extract_text("tests/sample.txt")
    assert text and not error

def test_unsupported_file():
    text, error = extract_text("tests/sample.unsupported")
    assert text is None and "Unsupported" in error 