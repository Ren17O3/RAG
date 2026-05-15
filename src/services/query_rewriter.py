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
    max_new_tokens=64,
    temperature=0.1,
    do_sample=False,
)


chat_model = ChatHuggingFace(llm=llm)


def rewrite_query(query: str) -> str:
    """
    Rewrite student queries into
    clearer retrieval-friendly queries.
    """

    prompt = f"""
You are a query rewriting assistant
for a syllabus-based RAG system.

Your job:
- If the query is casual conversation,
    greeting, or unrelated to academics,
    return the original query unchanged.
-Else, rewrite the query to be more specific and clear for retrieval.
- Expand abbreviations
- Improve clarity for retrieval
- Preserve original meaning
- Keep concise
- Return ONLY a single string which is the rewritten query

Examples:

Student Query:
what is util

Rewritten Query:
What is utilitarian theory in ethics?

Student Query:
oop pillars

Rewritten Query:
What are the four pillars of object-oriented programming?

Student Query:
db normalization explain 

Rewritten Query:
Explain database normalization.

Student Query:
{query}

Rewritten Query:
"""

    response = chat_model.invoke(prompt)

    rewritten_query = response.content.strip()

    return rewritten_query
