# Phase 3: Semantic Retrieval, Conversational Memory & FastAPI Endpoints

This document covers **Phase 3** of developing the **AI-Powered Contextual Website Chatbot with Memory (EduMind RAG SaaS)**.

---

## 1. Overview & Objectives

Phase 3 implements the core RAG runtime and REST endpoints:
- **Semantic Vector Retrieval**: Given a user query, generate query embeddings and retrieve top-5 relevant chunks from Pinecone.
- **Conversational Memory**: Fetch session-based conversation history from Supabase to handle follow-up context.
- **Prompt Engineering & OpenAI LLM Generation**: Construct strict context-grounded prompts ensuring zero hallucination.
- **FastAPI Endpoints**: Expose API contracts for chat, document ingestion, history retrieval, document deletion, and FAQ management.

---

## 2. Conversational Memory Manager (`backend/memory.py`)

Create `backend/memory.py` to retrieve and format previous interactions:

```python
from backend.database import fetch_chat_history

class ConversationMemoryManager:
    @staticmethod
    def get_formatted_memory(user_id: str, limit: int = 5) -> str:
        """
        Retrieves past conversation items and formats them into a conversation history string.
        """
        history_records = fetch_chat_history(user_id=user_id, limit=limit)
        if not history_records:
            return "No previous conversation history."

        formatted_lines = []
        for item in history_records:
            formatted_lines.append(f"User: {item['question']}")
            formatted_lines.append(f"Assistant: {item['answer']}")

        return "\n".join(formatted_lines)
```

---

## 3. RAG Engine & Prompt Assembly (`backend/rag.py`)

Create `backend/rag.py` to perform semantic search, prompt injection, and OpenAI API completion:

```python
import os
import openai
from dotenv import load_dotenv
from backend.embeddings import embedding_engine
from backend.pinecone_db import pinecone_client
from backend.memory import ConversationMemoryManager
from backend.database import save_chat_message

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_TEMPLATE = """You are an intelligent educational assistant (EduMind AI).

Use ONLY the provided retrieved context and conversation history to answer the user's question. 
If the answer cannot be determined strictly from the provided context, state clearly: "I cannot find relevant information in the uploaded documents to answer your question." Do not make up facts or hallucinate.

Conversation History:
{memory}

Retrieved Context Chunks:
{chunks}

Question:
{query}

Generate a clear, accurate, and context-grounded answer:"""

class RAGEngine:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def generate_response(self, user_id: str, query: str) -> dict:
        # 1. Generate Query Vector Embedding
        query_embedding = embedding_engine.generate_embedding(query)

        # 2. Query Pinecone Vector Database
        search_results = pinecone_client.query_similarity(vector=query_embedding, top_k=self.top_k)
        
        matches = search_results.get("matches", [])
        retrieved_chunks = []
        sources = []

        for match in matches:
            metadata = match.get("metadata", {})
            text_chunk = metadata.get("text", "")
            file_name = metadata.get("file_name", "Unknown File")
            score = match.get("score", 0.0)
            
            if text_chunk:
                retrieved_chunks.append(text_chunk)
                sources.append({
                    "file_name": file_name,
                    "score": round(score, 4),
                    "chunk": text_chunk[:150] + "..."
                })

        context_str = "\n\n---\n\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."

        # 3. Load Conversational Memory
        memory_str = ConversationMemoryManager.get_formatted_memory(user_id=user_id)

        # 4. Construct Prompt
        full_prompt = PROMPT_TEMPLATE.format(
            memory=memory_str,
            chunks=context_str,
            query=query
        )

        # 5. Invoke OpenAI LLM API
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful educational assistant."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Error generating answer from LLM: {str(e)}"

        # 6. Save Chat Message into Supabase
        save_chat_message(
            user_id=user_id,
            question=query,
            answer=answer,
            sources=sources
        )

        return {
            "answer": answer,
            "sources": sources,
            "chunks_retrieved": len(retrieved_chunks)
        }

rag_engine = RAGEngine()
```

---

## 4. FastAPI Server & API Endpoints (`backend/app.py`)

Create `backend/app.py` exposing REST APIs:

```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid

from backend.ingestion_service import process_and_ingest_document
from backend.rag import rag_engine
from backend.database import (
    fetch_all_documents,
    delete_document_record,
    fetch_chat_history,
    supabase
)
from backend.pinecone_db import pinecone_client

app = FastAPI(
    title="EduMind RAG SaaS API",
    description="Backend services for AI-Powered Contextual Website Chatbot with Memory",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / Response Schemas
class ChatRequest(BaseModel):
    user_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    chunks_retrieved: int

@app.get("/")
def read_root():
    return {"status": "online", "message": "EduMind RAG SaaS API is running."}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Form(None)
):
    try:
        contents = await file.read()
        result = process_and_ingest_document(
            file_bytes=contents,
            filename=file.filename,
            uploaded_by=uploaded_by
        )
        return {"message": "Document processed and stored successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    result = rag_engine.generate_response(
        user_id=request.user_id,
        query=request.question
    )
    return result

@app.get("/history")
def get_history(user_id: str):
    history = fetch_chat_history(user_id=user_id)
    return {"user_id": user_id, "history": history}

@app.delete("/history")
def clear_history(user_id: str):
    supabase.table("chat_history").delete().eq("user_id", user_id).execute()
    return {"message": f"Chat history for user {user_id} cleared successfully."}

@app.get("/documents")
def get_documents():
    docs = fetch_all_documents()
    return {"documents": docs}

@app.delete("/document/{document_id}")
def delete_document(document_id: str):
    try:
        # Delete vectors in Pinecone
        pinecone_client.delete_by_document(document_id)
        # Delete record in Supabase
        delete_document_record(document_id)
        return {"message": f"Document {document_id} and associated vectors deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 5. Verification Checklist

- [ ] Started server with `uvicorn backend.app:app --reload`.
- [ ] Navigated to `http://127.0.0.1:8000/docs` to verify OpenAPI Swagger documentation.
- [ ] Executed `POST /upload` with a sample PDF file and confirmed vector creation.
- [ ] Sent a query via `POST /chat` and verified grounded answer generation + sources return.
- [ ] Sent follow-up question ("Tell me more about it") and verified memory retention.
