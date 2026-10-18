from filingsiq.ingestion.chunker import chunk_text
from filingsiq.retrieval.hybrid import _or_query
from filingsiq.ingestion.parser import split_sections


def test_chunk_overlap():
    text = " ".join(str(i) for i in range(500))
    chunks = chunk_text(text, max_words=100, overlap=20)
    assert len(chunks) > 1
    assert chunks[0].split()[-20:] == chunks[1].split()[:20]


def test_keyword_query_removes_possessive_artifact():
    query = _or_query("How is Apple exposed to currency swings?")
    assert "s" not in query.split(" | ")
    assert "currency" in query


def test_split_sections():
    text = "Intro\nItem 1A. Risk Factors\nrisk text\nItem 7. MD&A\nmd&a text"
    labels = [s for s, _ in split_sections(text)]
    assert "Item 1A" in labels and "Item 7" in labels
