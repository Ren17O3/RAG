from pydantic import BaseModel
from typing import Optional


class DocumentRecord(BaseModel):
    text: str
    doc_name: str
    page: int
    source: str

    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    section_title: Optional[str] = None
    metadata: Optional[dict] = None


class ChunkRecord(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    doc_name: str
    page: int
    chunk_index: int

    metadata: Optional[dict] = None


class QueryRequest(BaseModel):
    session_id: str
    query: str
    documents: list[str] | None = None
