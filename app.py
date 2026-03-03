import shutil

import streamlit as st
import os

from src.ingest import load_documents
from src.chunk import chunk_documents
from src.embed import Embedder
from src.vector_store import VectorStore
from src.llm import generate_answer

@st.cache_resource
def get_embedder():
    return Embedder()


UPLOAD_DIR = "data/uploads"
INDEX_DIR = "data/index"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)




st.set_page_config(page_title="RAG", layout="wide")


st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Manage Data", "Ask Questions"]
)

def rebuild_index():
    existing_files = os.listdir(UPLOAD_DIR)

    if not existing_files:
        # Remove index if no documents remain
        if os.path.exists(INDEX_DIR):
            shutil.rmtree(INDEX_DIR)
        return

    progress = st.progress(0)
    status = st.empty()

    try:
        status.text("Loading documents...")
        records = load_documents([
            os.path.join(UPLOAD_DIR, f)
            for f in existing_files
        ])
        progress.progress(20)

        status.text("Chunking documents...")
        chunks = chunk_documents(records)
        progress.progress(40)

        status.text("Generating embeddings...")
        embedder = Embedder()
        embeddings = embedder.embed_texts([c["text"] for c in chunks])
        progress.progress(70)

        status.text("Building vector index...")
        store = VectorStore(embeddings.shape[1])
        store.add(embeddings, chunks)
        store.save(INDEX_DIR)
        progress.progress(100)

        status.success("Index rebuilt successfully")

    except Exception as e:
        status.error("Indexing failed")
        raise e



# -----------------------
# EXISTING FILES
# -----------------------
def render_data_page():
    st.header("Manage Documents")

    left_col, right_col = st.columns([3, 1])

    # -------------------------------
    # LEFT: FILE UPLOAD
    # -------------------------------
    with left_col:
        st.subheader("Upload files")

        uploaded_files = st.file_uploader(
            "Upload PDFs / PPTX",
            type=["pdf", "pptx"],
            accept_multiple_files=True
        )

        if uploaded_files:
            for file in uploaded_files:
                path = os.path.join(UPLOAD_DIR, file.name)
                with open(path, "wb") as f:
                    f.write(file.read())
            
            rebuild_index()

            st.success(f"{len(uploaded_files)} files uploaded successfully")

    # -------------------------------
    # RIGHT: EXISTING FILES
    # -------------------------------
    with right_col:
        st.subheader("Uploaded files")

        existing_files = os.listdir(UPLOAD_DIR)

        if not existing_files:
            st.info("No files uploaded")
        else:
            for file in existing_files:
                col1, col2 = st.columns([4, 1])
                col1.write(file)

                if col2.button("❌", key=f"delete_{file}"):
                    os.remove(os.path.join(UPLOAD_DIR, file))
                    st.warning(f"Deleted {file}")
                    rebuild_index()
                    st.rerun()


    
# -------------------------------
# CHAT BOT
# -------------------------------

def render_chat_page():
    st.title("Text-Bounded RAG System ChatBot")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"]) 
            
    prompt = st.chat_input("Ask Question")
    
    if prompt:
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        response = ""
        
        upload_files = os.listdir(UPLOAD_DIR)
        assistant_placeholder = st.empty()
        assistant_placeholder.empty()
        
        if not upload_files:
            response = "No documents uploaded. Please upload files first."

        elif not os.path.exists(os.path.join(INDEX_DIR, "index.faiss")):
            response = "Please build the index first"
        else:

            with st.spinner("..."):
                store = VectorStore.load(INDEX_DIR)
                embedder = Embedder()

                q_emb = embedder.embed_texts([prompt])
                results = store.search(q_emb, top_k=4)

                MAX_SCORE = max(r["score"] for r in results)
                print("MAX_SCORE", MAX_SCORE)
                if MAX_SCORE < 0.4:
                    response = "The uploaded material does not cover this topic."
                else:
                    context_chunks = [
                        f"[{r['doc_name']} | Page {r['page']}]\n{r['text']}"
                        for r in results
                    ]
                    response = generate_answer(context_chunks, prompt)
            
        with assistant_placeholder.container():
                with st.chat_message("assistant"):
                    st.markdown(response)
                    if (
                            "The uploaded material does not cover this topic." not in response
                            and "Please build the index first" not in response
                            and "No documents uploaded. Please upload files first." not in response
                        ):

                        st.markdown("Sources")
                        for i in range(0,2):
                            with st.expander(f"{results[i]['doc_name']} — Page {results[i]['page']}"):
                                st.write(results[i]["text"])
                    
                    

                st.session_state.messages.append({"role": "assistant", "content": response})
            # -------------------------------
            # OUTPUT
            # -------------------------------
        


    
if page == "Manage Data":
    render_data_page()

elif page == "Ask Questions":
    render_chat_page()

