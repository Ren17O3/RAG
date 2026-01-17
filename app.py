import streamlit as st
import os

from src.ingest import load_documents
from src.chunk import chunk_documents
from src.embed import Embedder
from src.vector_store import VectorStore
from src.llm import generate_answer




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



# -----------------------
# EXISTING FILES
# -----------------------
def render_data_page():
    st.header("Upload and Manage Documents")

    left_col, right_col = st.columns([3, 1])

    # -------------------------------
    # LEFT: FILE UPLOAD
    # -------------------------------
    with left_col:
        st.subheader("Upload files")

        uploaded_files = st.file_uploader(
            "Upload PDFs / PPT / PPTX",
            type=["pdf", "ppt", "pptx"],
            accept_multiple_files=True
        )

        if uploaded_files:
            for file in uploaded_files:
                path = os.path.join(UPLOAD_DIR, file.name)
                with open(path, "wb") as f:
                    f.write(file.read())

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
                    st.rerun()


    # -------------------------------
    # BUILD INDEX
    # -------------------------------
    st.header("Prepare Your Documents for Question Answering")

    if st.button("Build Index"):
        if not existing_files:
            st.warning("No files available to index")
        else:
            progress = st.progress(0)
            status = st.empty()

        try:
            # 1️⃣ Load documents
            status.text("Loading documents...")
            records = load_documents([
                os.path.join(UPLOAD_DIR, f)
                for f in existing_files
            ])
            progress.progress(20)

            # 2️⃣ Chunking
            status.text("Chunking documents...")
            chunks = chunk_documents(records)
            progress.progress(40)

            # 3️⃣ Embeddings (slow)
            status.text("Generating embeddings...")
            embedder = Embedder()
            embeddings = embedder.embed_texts([c["text"] for c in chunks])
            progress.progress(70)

            # 4️⃣ Build index
            status.text("Building vector index...")
            store = VectorStore(embeddings.shape[1])
            store.add(embeddings, chunks)
            store.save(INDEX_DIR)
            progress.progress(90)

            # 5️⃣ Save metadata
            status.text("Finalizing...")
            progress.progress(100)

            status.success("Index built successfully")

        except Exception as e:
            status.error("Indexing failed")
            raise e

    st.write("(Always Build Index after uploading/deleting files)")


# -------------------------------
# CHAT BOT
# -------------------------------
try:
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
            
            if not os.path.exists(os.path.join(INDEX_DIR, "index.faiss")):
                response = "Please build the index first"
            else:
                assistant_placeholder = st.empty()
                assistant_placeholder.empty()
                with st.spinner("..."):
                    store = VectorStore.load(INDEX_DIR)
                    embedder = Embedder()

                    q_emb = embedder.embed_texts([prompt])
                    results = store.search(q_emb, top_k=4)

                    MAX_SCORE = max(r["score"] for r in results)

                    if MAX_SCORE < 0.3:
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
                            ):

                            st.markdown("Sources")
                            for i in range(0,2):
                                with st.expander(f"{results[i]['doc_name']} — Page {results[i]['page']}"):
                                    st.write(results[i]["text"])
                        
                        

                    st.session_state.messages.append({"role": "assistant", "content": response})
                # -------------------------------
                # OUTPUT
                # -------------------------------
            
except Exception as e:
    error_msg = str(e).lower()

    if (
        "rate limit" in error_msg
        or "quota" in error_msg
        or "429" in error_msg
        or "resource_exhausted" in error_msg
    ):
        st.warning(
            "Rate limit reached. Please wait a moment and try again."
        )
    else:
        st.error("An unexpected error occurred. Please try again.")

        # Optional: show error details during development
        # st.caption(str(e))

    
if page == "Manage Data":
    render_data_page()

elif page == "Ask Questions":
    render_chat_page()

