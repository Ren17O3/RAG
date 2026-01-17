import faiss
import pickle
import os
import numpy as np


class VectorStore:
    def __init__(self, embedding_dim: int):
        # Inner Product index (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.records: list[dict] = []

    def add(self, embeddings: np.ndarray, records: list[dict]):
        """
        Add embeddings and their corresponding metadata records.
        Order MUST be preserved.
        """
        self.index.add(embeddings)
        self.records.extend(records)

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        """
        Search the index and return top_k matching chunks with metadata.
        """
        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            record = self.records[idx]
            results.append({
                "score": float(score),
                "text": record["text"],
                "doc_name": record["doc_name"],
                "page": record["page"]
            })

        return results

    def save(self, path: str):
        """
        Persist FAISS index and metadata to disk.
        """
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))

        with open(os.path.join(path, "records.pkl"), "wb") as f:
            pickle.dump(self.records, f)

    @classmethod
    def load(cls, path: str):
        """
        Load FAISS index and metadata from disk.
        """
        index = faiss.read_index(os.path.join(path, "index.faiss"))

        with open(os.path.join(path, "records.pkl"), "rb") as f:
            records = pickle.load(f)

        store = cls(index.d)
        store.index = index
        store.records = records
        return store
