# EduMind AI-Powered Contextual Website Chatbot with Memory

Welcome to **EduMind AI RAG SaaS**, an enterprise-grade website chatbot that leverages **Retrieval-Augmented Generation (RAG)**, dense vector embeddings, and session-based conversational memory to deliver accurate, grounded answers from uploaded course materials, documents, FAQs, and institutional knowledge bases.

---

## 🏗️ System Architecture & Technology Stack

- **Frontend Application**: Streamlit with custom Glassmorphism CSS design system (`frontend/streamlit_app.py`)
- **Backend API**: Python FastAPI (`backend/app.py`, Swagger UI at `/docs`)
- **Relational Database**: Supabase PostgreSQL (`backend/database.py`, `schema.sql`)
- **Vector Store**: Pinecone Serverless Vector Database (`backend/pinecone_db.py`, 384 dimensions, Cosine similarity metric)
- **Dense Embedding Model**: Google Gemini Embeddings API `text-embedding-004` (384-dim cloud embeddings, `backend/embeddings.py`)
- **LLM Synthesis**: Google Gemini API (`backend/rag.py`)

```
                         Admin User
                             │
                  Upload Document (PDF/DOCX/TXT/CSV)
                             │
                             ▼
                    FastAPI POST /upload
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
Text Processing & Chunking          Supabase Metadata Record
            │
Google Gemini Embeddings (384d)
            │
            ▼
   Pinecone Vector Store
===========================================================
                         End User
                             │
                      Ask Question
                             │
                             ▼
                    FastAPI POST /chat
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   Vector Search (Pinecone)      Conversational Memory (Supabase)
            │                                 │
            └────────────────┬────────────────┘
                             ▼
                  Prompt Engineering & Injection
                             │
                             ▼
                     Google Gemini Engine
                             │
                             ▼
                Context-Grounded Answer + Sources
```

---

## ⚙️ Admin Control Center & Document Lifecycle

The administrative interface ([`frontend/streamlit_app.py`](file:///c:/Users/HARSHITHA/edumind/frontend/streamlit_app.py)) provides full lifecycle management over chatbot training data:

### 1. Document Upload & Auto-Indexing (`POST /upload`)
- **Supported Formats**: `.pdf`, `.docx`, `.txt`, `.csv` (FAQ Q&A tables).
- **Processing Pipeline**:
  1. Validates file format and size.
  2. Extracts clean text using `pypdf2`, `python-docx`, or `pandas`.
  3. Splits text into 500-word chunks with 100-word overlap.
  4. Generates 384-dimensional dense embeddings via Hugging Face `all-MiniLM-L6-v2`.
  5. Upserts vectors directly into Pinecone.
  6. Records metadata (Title, file type, file size, chunk count, timestamp) in Supabase `documents` table.

### 2. Document Management & Purging (`GET /documents`, `DELETE /document/{id}`)
- Displays active knowledge documents in a structured grid/dataframe.
- **Synchronized Deletion**: Purging a document deletes all associated vector embeddings from Pinecone and removes the metadata record from Supabase to prevent orphan vectors.

### 3. Vector Store Analytics (`GET /admin/stats`)
- Live dashboard tab displaying total vector count, embedding dimension (384), similarity metric (`cosine`), index status, and cloud region specs.

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
- Python 3.10+ installed
- Git

### 2. Environment & Virtual Env Setup

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase, Pinecone, and Google Gemini API credentials:

```bash
cp .env.example .env
```

Environment config template (`.env`):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=edumind-knowledge-base

EMBEDDING_MODEL_NAME=text-embedding-004
EMBEDDING_DIMENSION=384

GOOGLE_API_KEY=your-google-api-key
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-flash-latest
```

---

## 🏃 Running the Application

### 1. Start Backend Server
Launch the FastAPI backend server with Uvicorn:

```bash
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

- **OpenAPI Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 2. Start Streamlit Glassmorphic Frontend Application
In a separate terminal, launch the Streamlit frontend:

```bash
streamlit run frontend/streamlit_app.py
```

Access the web interface in your browser at `http://localhost:8501`.

---

## 🧪 System Verification & Testing

Execute the automated system verification script to validate backend health, chat latency (<3.0s target), document listing, document ingestion, document deletion, Pinecone connectivity, and Supabase connectivity:

```bash
python verify_system.py
```

Example Verification Output:
```
==========================================================
   EDUMIND AI RAG CHATBOT - SYSTEM VERIFICATION SUITE   
==========================================================
  ✓ [PASS] Backend Health Endpoint (/health) (0.01s) - Status=healthy
  ✓ [PASS] Supabase Database Connectivity (0.00s) - Status=healthy
  ✓ [PASS] Pinecone Vector Store Connectivity (0.00s) - Status=healthy
  ✓ [PASS] Chat RAG Endpoint (POST /chat) (1.24s) - < 3.0s Target Met
  ✓ [PASS] Document Listing API (GET /documents) (0.05s) - Indexed Documents Count=2
  ✓ [PASS] Document Ingestion (POST /upload) (1.12s) - Uploaded 'system_verify_faq.txt'
  ✓ [PASS] Document Deletion (DELETE /document/{id}) (0.45s) - Purged document

==========================================================
   ALL 7/7 SYSTEM VERIFICATION CHECKS PASSED! [PASS]
==========================================================
```

---

## 🌐 Production Deployment Guide

### 1. Render Deployment (FastAPI Backend)

1. **Push Code to GitHub**:
   Ensure your code is committed and pushed to a GitHub repository. Verifying `.gitignore` is present so `.env` is **never** committed.

2. **Create Render Web Service**:
   - Log into [Render Dashboard](https://dashboard.render.com/).
   - Click **New +** -> **Blueprints** (or **Web Service**).
   - Select your `edumind` repository. Render automatically reads `render.yaml`.

3. **Configure Environment Variables**:
   In the Render Web Service **Environment** tab, set the following environment secrets:
   - `ENVIRONMENT` = `production`
   - `SUPABASE_URL` = `https://<your-supabase-id>.supabase.co`
   - `SUPABASE_ANON_KEY` = `<your-supabase-anon-key>`
   - `SUPABASE_SERVICE_ROLE_KEY` = `<your-supabase-service-role-key>`
   - `PINECONE_API_KEY` = `<your-pinecone-api-key>`
   - `PINECONE_INDEX_NAME` = `edumind-knowledge-base`
   - `PINECONE_CLOUD` = `aws`
   - `PINECONE_REGION` = `us-east-1`
   - `EMBEDDING_MODEL_NAME` = `sentence-transformers/all-MiniLM-L6-v2`
   - `EMBEDDING_DIMENSION` = `384`
   - `GEMINI_API_KEY` = `<your-gemini-api-key>`

4. **Verify Deployed API**:
   Once build completes, verify health at: `https://<your-backend-app>.onrender.com/health`

---

### 2. Streamlit Community Cloud Deployment (Frontend)

1. **Deploy to Streamlit Cloud**:
   - Log into [Streamlit Community Cloud](https://share.streamlit.io/).
   - Click **New app**, select your GitHub repository and branch.
   - Main file path: `frontend/streamlit_app.py`

2. **Set Backend URL Secret**:
   - Under **Advanced settings...** -> **Secrets**, add:
     ```toml
     BACKEND_URL = "https://<your-backend-app>.onrender.com"
     ```

3. **Deploy & Verify**:
   - Click **Deploy!**. Streamlit Cloud will build and launch your UI at `https://<your-app-name>.streamlit.app`.

---

## 📦 Core Dependencies

| Dependency | Purpose |
| :--- | :--- |
| `fastapi` | Asynchronous web framework for REST API endpoints |
| `streamlit` | Interactive client web framework |
| `uvicorn` | High-performance ASGI web server |
| `supabase` | Supabase SDK for PostgreSQL database & authentication |
| `pinecone-client` | Vector database SDK for embedding search & storage |
| `sentence-transformers` | Hugging Face local dense embeddings generator (`all-MiniLM-L6-v2`) |
| `google-genai` | Google Gemini API client for LLM completions |
| `pypdf2`, `python-docx`, `pandas` | Multi-format document text extraction engines |

---

## 📄 License & Credits
Developed for **EduMind AI RAG SaaS**.
