import uuid
import requests
import streamlit as st
import time

# -----------------------------------
# CONFIG
# -----------------------------------

API_BASE_URL = "https://rag-gt2l.onrender.com/api"

st.set_page_config(
    page_title="Syllabus RAG",
    layout="wide",
)


# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown(
    """
    <style>

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #0F172A;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    section[data-testid="stSidebar"] {
        background-color: #0B1220;
        border-right: 1px solid #334155;
    }

    h1, h2, h3 {
        color: #F8FAFC;
        font-weight: 700;
    }

    p, span, label {
        color: #E2E8F0;
    }

    .stChatMessage {
        border-radius: 16px;
        padding: 0.8rem;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 1rem;
        line-height: 1.7;
    }

    .stButton button {
        border-radius: 12px;
        border: none;
        background: linear-gradient(
            135deg,
            #7C3AED,
            #8B5CF6
        );
        color: white;
        font-weight: 600;
        padding: 0.65rem 1rem;
        width: auto;
    }

    .stButton button:hover {
        opacity: 0.92;
    }

    .upload-box {
        background: #1E293B;
        padding: 1rem;
        border-radius: 18px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }

    .answer-box {
        background: #111827;
        padding: 1rem;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-top: 1rem;
    }

    .rewrite-box {
        background: rgba(139, 92, 246, 0.12);
        padding: 0.8rem;
        border-radius: 12px;
        border-left: 4px solid #8B5CF6;
        margin-bottom: 1rem;
    }

    .source-box {
        background: #0B1220;
        padding: 0.55rem 0.8rem;
        border-radius: 10px;
        margin-bottom: 0.45rem;
        border: 1px solid #243244;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .hero-box {
        padding: 1.5rem;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #111827,
            #1E293B
        );
        border: 1px solid #334155;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
    }

    .hero-subtitle {
        color: #CBD5E1;
        margin-top: 0.5rem;
        font-size: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------
# STREAMING EFFECT
# -----------------------------------


def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.04)


# -----------------------------------
# SESSION STATE
# -----------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Manage Data", "Ask Questions"],
)

st.sidebar.divider()

st.sidebar.caption(f"Session ID: {st.session_state.session_id[:8]}")

# RESET BUTTON
if st.sidebar.button("🗑 Reset Session"):

    with st.spinner("Resetting session..."):

        response = requests.delete(
            f"{API_BASE_URL}/reset-session",
            params={"session_id": st.session_state.session_id},
            timeout=30,
        )

    if response.status_code == 200:

        st.session_state.messages = []

        st.session_state.session_id = str(uuid.uuid4())

        st.sidebar.success("Session reset successfully!")

        st.rerun()

    else:

        st.sidebar.error("Failed to reset session.")


# -----------------------------------
# DOCUMENT PAGE
# -----------------------------------


def render_data_page():

    st.markdown(
        """<div class="hero-box">
        <div class="hero-title">
            Document Management
        </div>
        <div class="hero-subtitle">
            Upload PDF and PPTX syllabus documents for retrieval-based question answering.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload PDF/PPTX files",
        type=["pdf", "pptx"],
        accept_multiple_files=True,
    )

    if uploaded_files:

        st.subheader("Selected Files")

        for file in uploaded_files:

            st.markdown(f"{file.name}")

    if st.button("Process Documents"):

        if not uploaded_files:

            st.warning("Please upload at least one file.")

            return

        files = []

        for file in uploaded_files:

            files.append(
                (
                    "files",
                    (
                        file.name,
                        file,
                        file.type,
                    ),
                )
            )

        with st.spinner("Processing documents..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/ingest",
                    params={"session_id": st.session_state.session_id},
                    files=files,
                    timeout=120,
                )
            except requests.RequestException as e:
                st.error("Failed to process documents, please try again.")
                return

        if response.status_code == 200:

            data = response.json()

            st.success("Documents processed successfully!")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Documents",
                data["documents_processed"],
            )

            col2.metric(
                "Chunks",
                data["chunks_created"],
            )

            col3.metric(
                "Vectors",
                data["vectors_stored"],
            )

        else:

            st.error("Failed to process documents, please try again.")


# -----------------------------------
# CHAT PAGE
# -----------------------------------


def render_chat_page():

    st.markdown(
        """
<div class="hero-box">
    <div class="hero-title">
        Syllabus RAG Assistant
    </div>
    <div class="hero-subtitle">
        Ask questions grounded strictly in your uploaded syllabus documents.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # -----------------------------------
    # FETCH DOCUMENTS
    # -----------------------------------

    available_documents = []

    try:

        documents_response = requests.get(
            f"{API_BASE_URL}/documents",
            params={"session_id": st.session_state.session_id},
            timeout=30,
        )

        if documents_response.status_code == 200:

            available_documents = documents_response.json().get("documents", [])

    except Exception:

        available_documents = []

    # -----------------------------------
    # SIDEBAR FILTERING
    # -----------------------------------

    st.sidebar.subheader("🔎 Search Filters")

    selected_documents = st.sidebar.multiselect(
        "Search Specific Documents",
        available_documents,
    )

    if not selected_documents:
        st.sidebar.caption("Searching all uploaded documents")
    else:
        st.sidebar.caption(f"Searching {len(selected_documents)} selected documents")
    # -----------------------------------
    # EMPTY STATE
    # -----------------------------------

    if not available_documents:

        st.info("Upload documents first before asking questions.")

        return

    # -----------------------------------
    # CHAT HISTORY
    # -----------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    prompt = st.chat_input("Ask a question...")

    if prompt:

        # -----------------------------------
        # USER MESSAGE
        # -----------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):

            st.markdown(prompt)

        # -----------------------------------
        # QUERY API
        # -----------------------------------

        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/query",
                    json={
                        "session_id": st.session_state.session_id,
                        "query": prompt,
                        "documents": selected_documents,
                    },
                    timeout=120,
                )
            except requests.RequestException as e:

                with st.chat_message("assistant"):

                    st.error("Query failed. Please try again.")

                return

        # -----------------------------------
        # REQUEST FAILURE
        # -----------------------------------

        data = response.json()

        # -----------------------------------
        # RESPONSE
        # -----------------------------------

        if "message" in data:

            assistant_response = data["message"]

        else:

            assistant_response = data["answer"]

        # -----------------------------------
        # ASSISTANT RESPONSE
        # -----------------------------------

        with st.chat_message("assistant"):

            # rewritten query
            if "rewritten_query" in data:

                rewritten_query = data["rewritten_query"]

                if rewritten_query.lower().strip() != prompt.lower().strip():

                    st.markdown(
                        f"""
                        <div class="rewrite-box">
                        <b>Rewritten Query</b><br>
                        {rewritten_query}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # streamed answer
            st.write_stream(stream_text(assistant_response))

            # citations
            if "answer" in data and "citations" in data:

                st.subheader("Sources")

                for citation in data["citations"][:3]:

                    st.markdown(
                        f"""
                        <div class="source-box">
                         <b>{citation['document']}, Page {citation['page']}</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # -----------------------------------
        # SAVE CHAT HISTORY
        # -----------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
            }
        )


# -----------------------------------
# ROUTING
# -----------------------------------

if page == "Manage Data":

    render_data_page()

elif page == "Ask Questions":

    render_chat_page()
