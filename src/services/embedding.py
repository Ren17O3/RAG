import numpy as np

from sentence_transformers import SentenceTransformer


class Embedder:

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):

        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Convert texts into normalized embedding vectors.
        """

        embeddings = self.model.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        )

        return embeddings.astype("float32")
