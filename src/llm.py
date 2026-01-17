import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
# Make sure GEMINI_API_KEY is set in your environment
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_answer(context_chunks, question: str) -> str:
    """
    Generate a syllabus-grounded answer using retrieved chunks.
    """

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are an academic assistant.

STRICT RULES:
- Use ONLY the provided context
- Do NOT use outside knowledge
- If the answer is fully present, answer clearly
- If partially present, say "The uploaded material partially cover this topic." and also give the answer(s) based on the context
- If not present, say "The uploaded material does not cover this topic."
- Always cite page numbers in the answer

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return response.text.strip()
