# Phase 4: Glassmorphic Chat Interface & Frontend Application

This document outlines **Phase 4** of developing the **AI-Powered Contextual Website Chatbot with Memory (EduMind RAG SaaS)**.

---

## 1. Overview & Objectives

Phase 4 builds the client-side user experience:
- **Glassmorphism Design System**: Inject modern dark-mode aesthetic (`#030712`), radial background ambient glows, glass containers, and neon highlights based on [design.md](file:///c:/Users/HARSHITHA/rag/design.md).
- **ChatGPT-Style Web Interface**: Build an interactive chat UI with message bubbles, typing indicators, suggested starter prompt pills, and real-time streaming response UI.
- **Source Citation Visualizer**: Display expandable source document chips showing the exact document, chunk text, and similarity confidence score for retrieved answers.
- **Session State Management**: Retain local conversation context and support memory reset.

---

## 2. Glassmorphism CSS Styling Integration

Inject the core design system CSS into the frontend application:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

:root {
  --bg-deep: #030712;
  --glass-bg: rgba(17, 24, 39, 0.55);
  --glass-border: rgba(255, 255, 255, 0.1);
  --accent-violet: #6366f1;
  --accent-cyan: #22d3ee;
  --accent-emerald: #10b981;
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
}

body {
  background-color: var(--bg-deep) !important;
  color: var(--text-primary) !important;
  font-family: 'Outfit', 'Inter', sans-serif !important;
  background-image: 
    radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.18) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(34, 211, 238, 0.15) 0px, transparent 50%),
    radial-gradient(at 50% 50%, rgba(147, 51, 234, 0.1) 0px, transparent 50%) !important;
  background-attachment: fixed !important;
}

/* Glassmorphism Container */
.glass-container {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
  padding: 1.5rem !important;
}

/* Chat Message Bubbles */
.chat-bubble-user {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
  color: #ffffff !important;
  border-radius: 18px 18px 2px 18px !important;
  padding: 12px 18px !important;
  margin-left: auto !important;
  max-width: 80% !important;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
}

.chat-bubble-assistant {
  background: rgba(31, 41, 55, 0.7) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #f9fafb !important;
  border-radius: 18px 18px 18px 2px !important;
  padding: 14px 20px !important;
  margin-right: auto !important;
  max-width: 85% !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

/* Source Citation Pill */
.source-chip {
  display: inline-block;
  background: rgba(34, 211, 238, 0.12);
  border: 1px solid rgba(34, 211, 238, 0.3);
  color: #22d3ee;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 0.75rem;
  margin: 4px 4px 0 0;
  font-weight: 500;
}
```

---

## 3. Frontend Chat Application (`frontend/streamlit_app.py`)

Create `frontend/streamlit_app.py` for the complete interactive UI:

```python
import streamlit as st
import requests
import uuid
import time

# API Configuration
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="EduMind AI - Contextual Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}
.stApp {
    background-color: #030712;
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(34, 211, 238, 0.12) 0px, transparent 50%);
}
.glass-header {
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
}
.prompt-btn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    color: #e5e7eb;
    padding: 8px 14px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.3s ease;
}
.prompt-btn:hover {
    background: rgba(99, 102, 241, 0.2);
    border-color: #6366f1;
}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Navigation
st.sidebar.title("🤖 EduMind RAG SaaS")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["💬 Chat Assistant", "📚 Knowledge Documents", "⚙️ Admin Control"])

st.sidebar.markdown("---")
st.sidebar.caption(f"Session ID: `{st.session_state.user_id[:8]}...`")
if st.sidebar.button("🗑️ Clear Chat History"):
    try:
        requests.delete(f"{BACKEND_URL}/history?user_id={st.session_state.user_id}")
        st.session_state.messages = []
        st.sidebar.success("Chat history cleared.")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error clearing history: {e}")

# Page 1: Chat Assistant
if page == "💬 Chat Assistant":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin:0; color:#f9fafb;">🧠 AI Contextual Website Chatbot</h1>
        <p style="margin:5px 0 0 0; color:#9ca3af;">Ask questions grounded strictly in your uploaded course materials, policies, and FAQs.</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggested Prompts
    st.write("💡 **Suggested Questions:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📚 What AI courses are offered?"):
            st.session_state.pending_prompt = "What AI courses are offered?"
    with col2:
        if st.button("💳 What is the tuition fee policy?"):
            st.session_state.pending_prompt = "What is the tuition fee policy?"
    with col3:
        if st.button("🕒 What are the submission deadlines?"):
            st.session_state.pending_prompt = "What are the submission deadlines?"

    # Display Message Feed
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("🔍 View Retrieved Sources"):
                    for src in message["sources"]:
                        st.markdown(f"**📄 {src['file_name']}** (Score: `{src['score']}`)")
                        st.caption(f"_{src['chunk']}_")

    # Chat Input
    prompt = st.chat_input("Ask any question about your documents...")
    if hasattr(st.session_state, 'pending_prompt'):
        prompt = st.session_state.pending_prompt
        del st.session_state.pending_prompt

    if prompt:
        # Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call Backend API
        with st.chat_message("assistant"):
            with st.spinner("Searching vector database & synthesizing answer..."):
                try:
                    payload = {
                        "user_id": st.session_state.user_id,
                        "question": prompt
                    }
                    res = requests.post(f"{BACKEND_URL}/chat", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        answer = data["answer"]
                        sources = data.get("sources", [])

                        st.markdown(answer)
                        if sources:
                            with st.expander("🔍 View Retrieved Sources"):
                                for src in sources:
                                    st.markdown(f"**📄 {src['file_name']}** (Score: `{src['score']}`)")
                                    st.caption(f"_{src['chunk']}_")

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                    else:
                        st.error(f"Error {res.status_code}: {res.json().get('detail', 'Failed to generate response')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend service: {str(e)}")

# Page 2: Knowledge Documents View
elif page == "📚 Knowledge Documents":
    st.title("📚 Active Knowledge Base Documents")
    st.write("Browse documents currently indexed in Pinecone and Supabase.")

    try:
        res = requests.get(f"{BACKEND_URL}/documents")
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            if docs:
                for doc in docs:
                    with st.container():
                        st.markdown(f"""
                        <div style="background:rgba(31, 41, 55, 0.5); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:15px; margin-bottom:10px;">
                            <h4 style="margin:0; color:#22d3ee;">📄 {doc['title']}</h4>
                            <p style="margin:5px 0; color:#9ca3af; font-size:0.85rem;">File Type: {doc['file_type'].upper()} | Chunks Indexed: {doc['chunk_count']} | Uploaded: {doc['uploaded_at'][:10]}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No documents uploaded yet.")
    except Exception as e:
        st.error(f"Failed to load documents: {e}")

# Page 3: Admin Control
elif page == "⚙️ Admin Control":
    st.title("⚙️ Admin Knowledge Management")
    st.write("Upload new documents to auto-update vector database embeddings.")

    uploaded_file = st.file_uploader("Upload PDF, DOCX, TXT or FAQ CSV", type=["pdf", "docx", "txt", "csv"])
    if uploaded_file is not None:
        if st.button("🚀 Process & Ingest Document"):
            with st.spinner("Extracting text, chunking, and upserting embeddings to Pinecone..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if res.status_code == 200:
                        st.success(f"Successfully processed `{uploaded_file.name}`!")
                        st.json(res.json())
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")
```

---

## 4. Verification Checklist

- [ ] Launched Streamlit application via `streamlit run frontend/streamlit_app.py`.
- [ ] Verified glassmorphism theme styling renders dark background with radial glows.
- [ ] Tested clicking suggested question pills to trigger automated chat query execution.
- [ ] Verified source citation expander renders source file names and similarity confidence metrics.
- [ ] Verified chat history reset button clears local and Supabase records.
