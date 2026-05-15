import uuid
from typing import Optional

from nltk.tokenize import sent_tokenize
from pydantic import BaseModel

from src.schemas.models import DocumentRecord
from src.schemas.models import ChunkRecord


def chunk_documents(
    records: list[DocumentRecord],
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[ChunkRecord]:
    """
    Sentence-aware page-bounded chunking.

    - Chunks NEVER cross page boundaries
    - Preserves semantic meaning better than character slicing
    - Maintains overlap between chunks
    """

    chunks = []

    for record in records:

        sentences = sent_tokenize(record.text)

        current_chunk = []
        current_length = 0

        chunk_index = 0

        for sentence in sentences:

            sentence_length = len(sentence)

            # if adding this sentence exceeds chunk size,
            # finalize current chunk
            if current_length + sentence_length > chunk_size and current_chunk:

                chunk_text = " ".join(current_chunk).strip()
                word_count = len(chunk_text.split())
                if word_count < 5:
                    continue
                chunks.append(
                    ChunkRecord(
                        chunk_id=str(uuid.uuid4()),
                        document_id=record.document_id,
                        text=chunk_text,
                        doc_name=record.doc_name,
                        page=record.page,
                        chunk_index=chunk_index,
                        metadata=record.metadata,
                    )
                )

                chunk_index += 1

                # overlap logic
                overlap_sentences = []
                overlap_length = 0

                for s in reversed(current_chunk):

                    overlap_length += len(s)

                    if overlap_length > overlap:
                        break

                    overlap_sentences.insert(0, s)

                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length

        # final chunk
        if current_chunk:

            chunk_text = " ".join(current_chunk).strip()
            word_count = len(chunk_text.split())

            if word_count < 5:
                continue
            chunks.append(
                ChunkRecord(
                    chunk_id=str(uuid.uuid4()),
                    document_id=record.document_id,
                    text=chunk_text,
                    doc_name=record.doc_name,
                    page=record.page,
                    chunk_index=chunk_index,
                    metadata=record.metadata,
                )
            )

    return chunks
