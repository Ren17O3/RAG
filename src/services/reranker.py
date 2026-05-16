from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):

        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, query: str, results: list):

        pairs = [(query, result["chunk"].text) for result in results]

        scores = self.model.predict(pairs)

        reranked = []

        for score, result in zip(scores, results):

            reranked.append({"score": float(score), "chunk": result["chunk"]})

        reranked.sort(key=lambda x: x["score"], reverse=True)

        return reranked
