from fastapi import APIRouter

from src.schemas.models import QueryRequest

from src.services.retrieval import Retriever

from src.services.generator import generate_answer

from src.services.query_rewriter import rewrite_query

router = APIRouter()

retriever = Retriever()


@router.post("/query")
async def query_documents(request: QueryRequest):

    original_query = request.query

    session_id = request.session_id

    # -----------------------------
    # QUERY REWRITING
    # -----------------------------

    rewritten_query = rewrite_query(original_query)

    # -----------------------------
    # RETRIEVAL
    # -----------------------------

    results = retriever.retrieve(
        session_id=session_id,
        query=rewritten_query,
        top_k=5,
        documents=request.documents,
    )

    # -----------------------------
    # OUT-OF-SYLLABUS REJECTION
    # -----------------------------

    if not results:

        return {
            "query": original_query,
            "rewritten_query": rewritten_query,
            "message": ("The uploaded material " "does not cover this topic."),
        }

    # -----------------------------
    # GENERATION
    # -----------------------------

    answer = generate_answer(context_chunks=results, question=rewritten_query)

    # -----------------------------
    # CITATIONS
    # -----------------------------

    citations = []

    seen = set()

    for result in results:

        chunk = result["chunk"]

        key = (chunk.doc_name, chunk.page)

        if key in seen:
            continue

        seen.add(key)

        citations.append({"document": chunk.doc_name, "page": chunk.page})

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------

    return {
        "query": original_query,
        "rewritten_query": rewritten_query,
        "answer": answer,
        "citations": citations,
    }
