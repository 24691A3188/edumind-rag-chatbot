# Phase 1: Backend Architecture, Supabase Database & Vector Store Initialization

This document covers **Phase 1** of developing the **AI-Powered Contextual Website Chatbot with Memory (EduMind RAG SaaS)**. 

---

## 1. Overview & Objectives

Phase 1 establishes the core backend infrastructure, database schemas, and vector store initialization:
- **Backend Framework**: Python FastAPI environment setup.
- **Relational Database**: Supabase PostgreSQL DDL tables for Users, Chat History, Uploaded Documents, and FAQs.
- **Security**: Row Level Security (RLS) policies and PostgreSQL triggers for profile synchronization.
- **Vector Store**: Pinecone Vector Index initialization tailored for 384-dimensional embeddings (`sentence-transformers/all-MiniLM-L6-v2`).

---

## 2. Project Directory Structure

Establish the following directory tree:

```
rag-chatbot/
├── backend/
│   ├── app.py              # Main FastAPI application entrypoint
│   ├── database.py         # Supabase client connection & operations
│   ├── pinecone_db.py      # Pinecone vector store wrapper
│   ├── embeddings.py       # SentenceTransformers embedding engine
│   ├── upload.py           # Document parsing & chunking service
│   ├── rag.py              # Retrieval-Augmented Generation pipeline
│   └── memory.py           # Conversational memory context builder
├── frontend/
│   └── streamlit_app.py    # Streamlit/React Chat & Admin interface
├── documents/              # Temporary file storage directory
├── requirements.txt        # Python dependency manifest
├── .env                    # System environment configuration
└── README.md
```

---

## 3. Dependency Configuration (`requirements.txt`)

Create `requirements.txt` in the root folder:

```text
fastapi>=0.104.0
uvicorn>=0.24.0
supabase>=2.0.0
pinecone-client>=3.0.0
sentence-transformers>=2.2.2
openai>=1.3.0
pypdf2>=3.0.1
python-docx>=1.0.1
pandas>=2.1.0
python-dotenv>=1.0.0
pydantic>=2.4.0
python-multipart>=0.0.6
```

---

## 4. Environment Variables Setup (`.env`)

Create `.env` file in root:

```env
# Supabase Configuration
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_ANON_KEY=your-supabase-anon-key

# Pinecone Configuration
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=edumind-knowledge-base

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Embedding Model Configuration
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

---

## 5. Supabase Database Schema DDL (PostgreSQL)

Execute the following SQL commands inside the **Supabase SQL Editor**:

```sql
-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. USERS TABLE
create table public.users (
  id uuid references auth.users on delete cascade primary key,
  name text not null,
  email text unique not null,
  role text check (role in ('admin', 'student', 'customer', 'employee')) default 'student',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.users enable row level security;

-- 2. DOCUMENTS TABLE
create table public.documents (
  id uuid default uuid_generate_v4() primary key,
  title text not null,
  file_name text not null,
  file_type text not null,
  file_size integer,
  chunk_count integer default 0,
  uploaded_by uuid references public.users(id) on delete set null,
  uploaded_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.documents enable row level security;

-- 3. CHAT HISTORY TABLE
create table public.chat_history (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users(id) on delete cascade not null,
  question text not null,
  answer text not null,
  retrieved_sources jsonb default '[]'::jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.chat_history enable row level security;

-- 4. FAQ TABLE
create table public.faqs (
  id uuid default uuid_generate_v4() primary key,
  question text not null,
  answer text not null,
  category text default 'General',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.faqs enable row level security;

-- 5. AUTOMATED USER REGISTRATION TRIGGER
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, name, email, role)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'name', 'User'),
    new.email,
    coalesce(new.raw_user_meta_data->>'role', 'student')
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- 6. ROW LEVEL SECURITY (RLS) POLICIES
-- Users: Can read their own record or admins read all
create policy "Allow users read access" on public.users
  for select using (auth.uid() = id or (select role from public.users where id = auth.uid()) = 'admin');

-- Documents: Public read access, admin full access
create policy "Allow public read documents" on public.documents
  for select using (true);

create policy "Allow admin write documents" on public.documents
  for all using ((select role from public.users where id = auth.uid()) = 'admin');

-- Chat History: Users access only their own history
create policy "Allow users manage own chat history" on public.chat_history
  for all using (auth.uid() = user_id);

-- FAQs: Public read access, admin full access
create policy "Allow public read FAQs" on public.faqs
  for select using (true);

create policy "Allow admin manage FAQs" on public.faqs
  for all using ((select role from public.users where id = auth.uid()) = 'admin');
```

---

## 6. Vector Store Initialization (`backend/pinecone_db.py`)

Create `backend/pinecone_db.py` to handle index setup and vector operations:

```python
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "edumind-knowledge-base")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "384"))

class PineconeManager:
    def __init__(self):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self._ensure_index_exists()
        self.index = self.pc.Index(INDEX_NAME)

    def _ensure_index_exists(self):
        existing_indices = [idx.name for idx in self.pc.list_indexes()]
        if INDEX_NAME not in existing_indices:
            print(f"Creating Pinecone index '{INDEX_NAME}' with dim={EMBEDDING_DIM}...")
            self.pc.create_index(
                name=INDEX_NAME,
                dimension=EMBEDDING_DIM,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"Pinecone index '{INDEX_NAME}' created successfully.")

    def upsert_vectors(self, vectors):
        """
        vectors: list of tuples (id, embedding_list, metadata_dict)
        """
        return self.index.upsert(vectors=vectors)

    def query_similarity(self, vector, top_k=5, filter_dict=None):
        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )

    def delete_by_document(self, document_id):
        return self.index.delete(filter={"document_id": {"$eq": str(document_id)}})

    def get_stats(self):
        return self.index.describe_index_stats()

# Global Singleton Instance
pinecone_client = PineconeManager()
```

---

## 7. Database Service Wrapper (`backend/database.py`)

Create `backend/database.py` for Supabase CRUD operations:

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase configuration in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper functions
def record_document(title: str, file_name: str, file_type: str, file_size: int, chunk_count: int, uploaded_by: str = None):
    data = {
        "title": title,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": file_size,
        "chunk_count": chunk_count,
        "uploaded_by": uploaded_by
    }
    response = supabase.table("documents").insert(data).execute()
    return response.data[0] if response.data else None

def fetch_all_documents():
    return supabase.table("documents").select("*").order("uploaded_at", desc=True).execute().data

def delete_document_record(document_id: str):
    return supabase.table("documents").delete().eq("id", document_id).execute()

def save_chat_message(user_id: str, question: str, answer: str, sources: list):
    data = {
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "retrieved_sources": sources
    }
    return supabase.table("chat_history").insert(data).execute()

def fetch_chat_history(user_id: str, limit: int = 10):
    return supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at", desc=False).limit(limit).execute().data
```

---

## 8. Verification Checklist

- [ ] Python virtual environment initialized (`python -m venv venv`).
- [ ] Dependencies installed via `pip install -r requirements.txt`.
- [ ] `.env` file populated with valid Supabase, Pinecone, and OpenAI credentials.
- [ ] DDL SQL scripts executed in Supabase console without syntax errors.
- [ ] Verified table creation: `users`, `documents`, `chat_history`, `faqs`.
- [ ] Executed `python backend/pinecone_db.py` to confirm Pinecone index creation.
