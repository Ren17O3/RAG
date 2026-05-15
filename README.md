# 📚 Syllabus-Bounded RAG Assistant

A retrieval-augmented academic assistant that answers questions strictly from uploaded syllabus documents.

Built using **FastAPI**, **FAISS**, **Sentence Transformers**, and **Streamlit**, this project focuses on grounded retrieval, bounded responses, and a clean student-friendly experience.

---

# ✨ Features

## 🔍 Syllabus-Bounded Retrieval

* Answers are generated strictly from uploaded PDF/PPTX documents
* Prevents unrelated hallucinated responses
* Rejects out-of-syllabus queries gracefully

## 📄 Multi-Document Upload

* Upload multiple:

  * PDFs
  * PPTX files
* Automatic ingestion and indexing pipeline

## 🧠 Semantic Search Pipeline

* Sentence Transformer embeddings
* FAISS vector similarity search
* Cross-encoder reranking for improved relevance

## ✍️ Query Rewriting

* Student queries are rewritten into retrieval-friendly academic queries
* Optimized queries are shown transparently in the UI

## 🎯 Bounded Document Search

* Search across:

  * all uploaded documents
  * selected documents only
* Helpful for focused syllabus exploration

## 🧩 Session Isolation

Each user session gets:

* isolated vector storage
* isolated retrieval pipeline
* isolated uploaded documents

## 📚 Citation Support

Every generated answer includes:

* source document
* page references

## 🎨 Clean Streamlit Frontend

* Dark modern UI
* Responsive layout
* Streaming responses
* Retrieval transparency

---

# 🏗️ Architecture

```text
Frontend (Streamlit)
        ↓
FastAPI REST API
        ↓
Ingestion Pipeline
        ↓
Chunking
        ↓
Embeddings (BGE)
        ↓
FAISS Vector Store
        ↓
Retriever + Reranker
        ↓
LLM Generation
```

---

# ⚙️ Tech Stack

## Backend

* FastAPI
* FAISS
* Sentence Transformers
* HuggingFace Inference API
* Cross-Encoder Reranker

## Frontend

* Streamlit

## Models

* BAAI/bge-small-en-v1.5
* Qwen/Qwen3-4B-Instruct-2507
* cross-encoder/ms-marco-MiniLM-L-6-v2

---

# 📂 Project Structure

```text
.
├── frontend/
│   └── app.py
│
├── src/
│   ├── api/
│   │   ├── ingest.py
│   │   ├── query.py
│   │   └── documents.py
│   │
│   ├── core/
│   │   ├── store.py
│   │   └── store_manager.py
│   │
│   ├── schemas/
│   │   └── models.py
│   │
│   ├── services/
│   │   ├── chunking.py
│   │   ├── embedding.py
│   │   ├── ingestion.py
│   │   ├── llm.py
│   │   ├── query_rewriter.py
│   │   ├── reranker.py
│   │   ├── retrieval.py
│   │   └── vector_store.py
│   │
│   └── main.py
│
├── storage/
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/syllabus-rag.git

cd syllabus-rag
```

---

## 2. Create Virtual Environment

### Using uv

```bash
uv venv
```

Activate environment:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file:

```env
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

---

# ▶️ Running the Application

## Start FastAPI Backend

```bash
uvicorn src.main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

## Start Streamlit Frontend

```bash
streamlit run frontend/app.py
```

Frontend runs on:

```text
http://localhost:8501
```

---

# 🌐 API Endpoints

## Upload Documents

```http
POST /api/ingest
```

Uploads and indexes PDF/PPTX documents.

---

## Query Documents

```http
POST /api/query
```

Retrieves relevant chunks and generates syllabus-grounded answers.

---

## Get Uploaded Documents

```http
GET /api/documents
```

Returns uploaded documents for the active session.

---

## Reset Session

```http
DELETE /api/reset-session
```

Deletes session vector store and uploaded documents.

---

# 🧠 Retrieval Pipeline

## Step 1 — Document Ingestion

* Extract text from:

  * PDFs
  * PPTX files

## Step 2 — Chunking

* Documents are split into semantic chunks

## Step 3 — Embedding

* Chunks embedded using BGE embeddings

## Step 4 — Vector Search

* FAISS performs cosine similarity retrieval

## Step 5 — Reranking

* Cross-encoder reranks retrieved chunks

## Step 6 — Answer Generation

* Qwen LLM generates grounded responses

## Step 7 — Session Cleanup

* Old session vector stores are automatically cleaned up
* Prevents uncontrolled storage growth
* Keeps deployment lightweight and scalable for student usage

---

# 🛡️ Hallucination Reduction Strategy

The system reduces hallucinations using:

* syllabus-bounded retrieval
* similarity threshold rejection
* reranking validation
* grounded prompting
* citation generation
* out-of-syllabus rejection responses

---

# 📸 Demo

## Upload Documents

* Upload syllabus PDFs/PPTX files
* Process documents into vector embeddings

## Ask Questions

Example:

```text
What are the phases of SDLC?
```

## Receive Grounded Answers

* cited answers
* page references
* rewritten query visibility

---

# 🔥 Future Improvements

* Persistent database storage
* Authentication system
* Cloud vector databases
* OCR support for scanned PDFs
* Hybrid BM25 + vector retrieval
* Conversation memory
* Advanced evaluation pipelines
* Instructor dashboards

---

# 📌 Deployment

## Backend

Deployed using:

* Render

## Frontend

Deployed using:

* Streamlit Community Cloud

---

# 🤝 Contributing

Pull requests and suggestions are welcome.

If you'd like to improve:

* retrieval quality
* UI/UX
* evaluation
* performance

feel free to open an issue or PR.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

Built by Abhijai.
