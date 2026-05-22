from pathlib import Path

from fincontract.knowledge.ingest import chunk_text, load_documents


def test_load_documents_from_yaml(tmp_path: Path) -> None:
    content = (
        "version: 1\n"
        "documents:\n"
        "  - doc_id: TEST_DOC\n"
        "    title: Test Doc\n"
        "    version: 2024-01\n"
        "    effective_date: 2024-02-01\n"
        "    source: https://example.com\n"
        "    url: https://example.com/doc.html\n"
        "    format: html\n"
        "    category: test\n"
        "    enabled: true\n"
    )
    path = tmp_path / "documents.yaml"
    path.write_text(content, encoding="utf-8")

    docs = load_documents(path)
    assert len(docs) == 1
    assert docs[0].doc_id == "TEST_DOC"


def test_chunk_text_respects_max_chars() -> None:
    text = "Paragraph one. " * 50
    chunks = chunk_text(text, max_chars=100, min_chars=50)
    assert chunks
    assert all(len(chunk) <= 150 for chunk in chunks)
