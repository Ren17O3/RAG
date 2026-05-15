from src.core.store_manager import load_or_create_store

from src.services.embedding import Embedder

from src.services.reranker import Reranker


class Retriever:

    def __init__(self):

        self.embedder = Embedder()

        self.reranker = Reranker()

        self.similarity_threshold = 0.60

    def retrieve(self, session_id: str, query: str, top_k: int = 10, documents=None):

        vector_store = load_or_create_store(session_id)

        # --------------------------------
        # QUERY EMBEDDING
        # --------------------------------

        query_embedding = self.embedder.embed_texts([query])[0]

        # --------------------------------
        # VECTOR RETRIEVAL
        # --------------------------------

        retrieved_results = vector_store.search(
            query_embedding=query_embedding, top_k=top_k
        )

        # --------------------------------
        # DOCUMENT FILTERING
        # --------------------------------

        if documents:

            retrieved_results = [
                r for r in retrieved_results if (r["chunk"].doc_name in documents)
            ]

        # --------------------------------
        # NO RESULTS
        # --------------------------------

        if not retrieved_results:

            return []

        # --------------------------------
        # THRESHOLD REJECTION
        # --------------------------------

        top_score = retrieved_results[0]["score"]

        if top_score < self.similarity_threshold:

            return []

        # --------------------------------
        # RERANKING
        # --------------------------------

        reranked_results = self.reranker.rerank(query=query, results=retrieved_results)

        return reranked_results[:5]
