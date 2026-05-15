import os

from src.services.vector_store import VectorStore
from src.utils.cleanup import cleanup_old_sessions

BASE_STORAGE_PATH = "storage/sessions"


def get_session_store_path(session_id: str) -> str:

    return os.path.join(BASE_STORAGE_PATH, session_id)


def load_or_create_store(session_id: str) -> VectorStore:
    cleanup_old_sessions()
    store_path = get_session_store_path(session_id)

    index_path = os.path.join(store_path, "index.faiss")

    # existing store
    if os.path.exists(index_path):

        return VectorStore.load(store_path)

    # new store
    os.makedirs(store_path, exist_ok=True)

    return VectorStore(embedding_dim=384)
