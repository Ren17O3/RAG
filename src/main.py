from ingest import load_documents
from chunk import chunk_documents
from embed import Embedder
from vector_store import VectorStore
from llm import generate_answer

# Build index (run once)
records = load_documents(["data/AI & ML DIGITAL NOTES.pdf"])
chunks = chunk_documents(records)

embedder = Embedder()
embeddings = embedder.embed_texts([c["text"] for c in chunks])

store = VectorStore(embeddings.shape[1])
store.add(embeddings, chunks)
store.save("data/index")

# Query time
store = VectorStore.load("data/index")

question = "What is deep learning?"

q_emb = embedder.embed_texts([question])
results = store.search(q_emb, top_k=3)

context_chunks = [
    f"[{r['doc_name']} | Page {r['page']}]\n{r['text']}"
    for r in results
]

answer = generate_answer(context_chunks, question)

print(answer)
