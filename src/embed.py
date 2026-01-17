import numpy as np
from sentence_transformers import SentenceTransformer
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts):
        """
        Convert a list of texts into embedding vectors.
        """
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True
        )

        return np.array(embeddings, dtype="float32")
