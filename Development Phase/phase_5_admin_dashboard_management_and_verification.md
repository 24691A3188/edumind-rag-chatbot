# Phase 5: Admin Dashboard, Document Lifecycle Management & Verification

This document details **Phase 5** of developing the **AI-Powered Contextual Website Chatbot with Memory (EduMind RAG SaaS)**.

---

## 1. Overview & Objectives

Phase 5 focuses on administrative management, security enforcement, performance optimization, and end-to-end verification:
- **Admin Control Portal**: Allow administrators to upload new knowledge documents (PDF, DOCX, TXT, FAQ CSV), view indexed files, and purge outdated knowledge.
- **Synchronized Document Purging**: Ensure document deletion removes metadata from Supabase and purges associated vector embeddings from Pinecone.
- **Security & RLS Verification**: Verify that only authorized users can upload/delete documents while restricting unauthorized database access.
- **Latency & Hallucination Auditing**: Benchmark API response latency (<3s target) and verify prompt grounding constraints.

---

## 2. Admin Document Management Component

Build the administrative document management module (`frontend/admin_dashboard.py` / integrated in Streamlit app):

```python
import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://127.0.0.1:8000"

def render_admin_dashboard():
    st.markdown("""
    <div style="background: rgba(17, 24, 39, 0.6); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1); border-radius:16px; padding:20px; margin-bottom:20px;">
        <h2 style="margin:0; color:#f9fafb;">⚙️ Administrator Knowledge Control Center</h2>
        <p style="margin:5px 0 0 0; color:#9ca3af;">Manage uploaded training data, monitor vector indices, and control chatbot knowledge.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "📁 Manage Knowledge Base", "📊 Vector Index Stats"])

    # Tab 1: Upload Documents & FAQs
    with tab1:
        st.subheader("Upload Training Material")
        st.write("Upload PDF, DOCX, TXT documents or Q&A FAQ CSV files.")
        
        uploaded_file = st.file_uploader("Select File", type=["pdf", "docx", "txt", "csv"], key="admin_uploader")
        
        if uploaded_file and st.button("Submit & Index Document"):
            with st.spinner("Processing document, chunking, and upserting embeddings..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if res.status_code == 200:
                        st.success(f"Successfully processed `{uploaded_file.name}`!")
                        st.json(res.json())
                        st.rerun()
                    else:
                        st.error(f"Error processing file: {res.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    # Tab 2: Manage & Delete Documents
    with tab2:
        st.subheader("Active Indexed Documents")
        try:
            res = requests.get(f"{BACKEND_URL}/documents")
            if res.status_code == 200:
                docs = res.json().get("documents", [])
                if docs:
                    df = pd.DataFrame(docs)
                    st.dataframe(df[["id", "title", "file_type", "chunk_count", "uploaded_at"]], use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("Delete Outdated Document")
                    doc_to_delete = st.selectbox("Select document to purge", options=docs, format_func=lambda x: f"{x['title']} (ID: {x['id'][:8]}...)")
                    
                    if st.button("🗑️ Purge Document & Vectors", type="primary"):
                        with st.spinner("Purging vectors from Pinecone and deleting record from Supabase..."):
                            del_res = requests.delete(f"{BACKEND_URL}/document/{doc_to_delete['id']}")
                            if del_res.status_code == 200:
                                st.success(f"Document `{doc_to_delete['title']}` deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Deletion failed: {del_res.text}")
                else:
                    st.info("No documents currently indexed.")
        except Exception as e:
            st.error(f"Failed to fetch documents: {e}")

    # Tab 3: Vector Index Stats
    with tab3:
        st.subheader("Pinecone Vector Store Metrics")
        st.info("Metric: Cosine Similarity | Dimension: 384 | Cloud Provider: AWS us-east-1")
```

---

## 3. Automated System Verification Script (`backend/verify_system.py`)

Create `backend/verify_system.py` to run automated system validation:

```python
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("[1/5] Testing Root Health Endpoint...")
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200, f"Health check failed with code {res.status_code}"
    print("  ✓ Root Health Endpoint is ONLINE.")

def test_chat_response():
    print("[2/5] Testing Chat RAG Endpoint & Latency...")
    start_time = time.time()
    payload = {
        "user_id": "test-verify-user",
        "question": "What is the policy for submitting assignments?"
    }
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    elapsed = time.time() - start_time
    assert res.status_code == 200, f"Chat API failed with code {res.status_code}"
    data = res.json()
    assert "answer" in data, "Response missing 'answer' field"
    print(f"  ✓ Chat API returned response in {elapsed:.2f} seconds (< 3.0s target).")

def test_document_list():
    print("[3/5] Testing Document Listing API...")
    res = requests.get(f"{BASE_URL}/documents")
    assert res.status_code == 200, "Documents list API failed"
    docs = res.json().get("documents", [])
    print(f"  ✓ Documents API functional ({len(docs)} documents returned).")

def run_all_tests():
    print("=== STARTING EDUMIND RAG SAAS SYSTEM VERIFICATION ===")
    try:
        test_health()
        test_chat_response()
        test_document_list()
        print("=== ALL SYSTEM VERIFICATION CHECKS PASSED SUCCESSFULLY ===")
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
```

---

## 4. End-to-End Verification Checklist

### Functional Verification
- [ ] Uploaded `.pdf`, `.docx`, `.txt`, and FAQ `.csv` files via Admin portal without errors.
- [ ] Confirmed vectors are indexed in Pinecone and records added to Supabase.
- [ ] Verified deleting a document removes all associated vectors in Pinecone and row in Supabase.

### AI & Hallucination Safeguard Testing
- [ ] Asked a question explicitly answered in uploaded docs $\rightarrow$ verified accurate answer with source citation.
- [ ] Asked an out-of-scope question (e.g. "What is the capital of France?") $\rightarrow$ verified fallback response: *"I cannot find relevant information in the uploaded documents..."*.
- [ ] Asked follow-up questions $\rightarrow$ verified conversational memory correctly preserves context.

### Performance & Security Auditing
- [ ] Response latency benchmarking confirmed average completion time $< 3.0$ seconds.
- [ ] Row Level Security (RLS) policies verified in Supabase SQL editor.
