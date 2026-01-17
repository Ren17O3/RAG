def chunk_documents(
    records: list[dict],
    chunk_size: int = 500,
    overlap: int = 100
) -> list[dict]:
    """
    Page-bounded sliding window chunking.
    Chunks NEVER cross page boundaries.
    """

    chunks = []

    for record in records:
        text = record["text"]
        doc_name = record["doc_name"]
        page = record["page"]

        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "doc_name": doc_name,
                    "page": page
                })

            start += chunk_size - overlap

    return chunks
