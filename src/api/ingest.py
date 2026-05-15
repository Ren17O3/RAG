from typing import Annotated
from fastapi import APIRouter, UploadFile, File, HTTPException

import tempfile
import os

from src.services.ingestion import load_documents
from src.services.chunking import chunk_documents
from src.services.embedding import Embedder

from typing import List

from src.core.store_manager import load_or_create_store, get_session_store_path

router = APIRouter()

embedder = Embedder()

ALLOWED_EXTENSIONS = [".pdf", ".pptx"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/ingest")
async def ingest_documents(
    session_id: str, files: Annotated[List[UploadFile], File(...)]
):

    temp_files = []

    try:

        for file in files:

            ext = os.path.splitext(file.filename)[1].lower()

            if ext not in ALLOWED_EXTENSIONS:

                raise HTTPException(
                    status_code=400, detail=f"Unsupported file type: {file.filename}"
                )

            contents = await file.read()

            if len(contents) > MAX_FILE_SIZE:

                raise HTTPException(
                    status_code=400, detail=f"{file.filename} exceeds size limit"
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:

                temp_file.write(contents)

                temp_files.append(
                    {"temp_path": temp_file.name, "original_name": file.filename}
                )

        # extraction
        records = load_documents(temp_files)

        # chunking
        chunks = chunk_documents(records)

        # embeddings
        texts = [chunk.text for chunk in chunks]

        embeddings = embedder.embed_texts(texts)

        # vector store
        vector_store = load_or_create_store(session_id)
        vector_store.add(embeddings=embeddings, records=chunks)
        store_path = get_session_store_path(session_id)
        vector_store.save(store_path)

        return {
            "status": "success",
            "documents_processed": len(files),
            "records_extracted": len(records),
            "chunks_created": len(chunks),
            "vectors_stored": len(chunks),
        }

    finally:

        for file_info in temp_files:

            if os.path.exists(file_info["temp_path"]):
                os.remove(file_info["temp_path"])
