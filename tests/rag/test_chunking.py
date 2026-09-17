from enterpriseops_ai.rag.chunking import DocumentChunker


def test_split_respects_chunk_size() -> None:
    text = (
        "Purchase orders must be reviewed when delivery dates are missed.\n\n"
        "Supplier incidents should be escalated when they affect critical orders.\n\n"
        "Procurement teams must document the evidence used during an investigation."
    )

    chunker = DocumentChunker(
        chunk_size=100,
        chunk_overlap=0,
    )

    chunks = chunker.split(text)

    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)
    assert all(len(chunk) <= 100 for chunk in chunks)
