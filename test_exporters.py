from legal_ease.exporters import format_docx, format_pdf, format_txt


def test_txt_export():
    result = format_txt("# NDA\n\nConfidentiality")
    assert result.startswith(b"# NDA")


def test_docx_export_is_nonempty():
    result = format_docx("# NDA\n\nConfidentiality", "NDA")
    assert result[:2] == b"PK"
    assert len(result) > 1000


def test_pdf_export_is_nonempty():
    result = format_pdf("# NDA\n\nConfidentiality", "NDA")
    assert result.startswith(b"%PDF")
    assert len(result) > 500
