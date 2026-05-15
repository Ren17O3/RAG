import numpy as np

from sentence_transformers import SentenceTransformer


class Embedder:

    _model = None

    @classmethod
    def get_model(cls):

        if cls._model is None:

            cls._model = SentenceTransformer("BAAI/bge-small-en-v1.5")

        return cls._model

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Convert texts into normalized embedding vectors.
        """

        embeddings = self.model.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        )

        return embeddings.astype("float32")
