import os

from dotenv import load_dotenv

from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEndpoint,
)

load_dotenv()


llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY"),
    task="text-generation",
    max_new_tokens=256,
    temperature=0.1,
    do_sample=False,
)


chat_model = ChatHuggingFace(llm=llm)


def generate_answer(context_chunks, question: str) -> str:
    """
    Generate a syllabus-grounded answer
    using retrieved chunks.
    """

    # use only top reranked chunks
    top_chunks = context_chunks[:3]

    context_parts = []

    for result in top_chunks:

        chunk = result["chunk"]

        context_parts.append(f"""
Document: {chunk.doc_name}
Page: {chunk.page}

Content:
{chunk.text}
""")

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a syllabus-bounded academic assistant.

STRICT RULES:
- Use ONLY the provided context
- Do NOT use outside knowledge
- Check if the question is academic or casual, if its casual conversate and direct towards academics. IF its academic, answer using the context.  
- If the answer is fully present, answer clearly
- If partially present, say:
  "The uploaded material partially covers this topic."
  Then provide the available answer
- If the answer is not present, say:
  "The uploaded material does not cover this topic."
- Keep answers concise and factual
- Cite sources in this format:
  (Page <page>, <document>)

Question:
{question}

Context:
{context}

Answer:
"""

    response = chat_model.invoke(prompt)

    return response.content.strip()
