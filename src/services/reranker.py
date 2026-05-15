from sentence_transformers import CrossEncoder


class Reranker:

    _model = None

    @classmethod
    def get_model(cls):

        if cls._model is None:

            cls._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        return cls._model

    def rerank(self, query: str, results: list):

        pairs = [(query, result["chunk"].text) for result in results]

        scores = self.model.predict(pairs)

        reranked = []

        for score, result in zip(scores, results):

            reranked.append({"score": float(score), "chunk": result["chunk"]})

        reranked.sort(key=lambda x: x["score"], reverse=True)

        return reranked
