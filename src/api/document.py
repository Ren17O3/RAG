from fastapi import APIRouter

from src.core.store_manager import load_or_create_store

router = APIRouter()


@router.get("/documents")
async def get_documents(session_id: str):
    """
    Return all uploaded document names
    for the current session.
    """

    vector_store = load_or_create_store(session_id)

    documents = list({record.doc_name for record in vector_store.records})

    documents.sort()

    return {"documents": documents}
