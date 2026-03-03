import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    huggingfacehub_api_token=f"{os.getenv('HUGGINGFACE_API_KEY')}",
    task="text-generation",
    max_new_tokens=256,
    temperature=0.7,
)

chat_model = ChatHuggingFace(llm=llm)



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

    response = chat_model.invoke(prompt)

    return response.text.strip()
