# Phase 2: Document Processing & Embedding Ingestion Pipeline

This document details **Phase 2** of developing the **AI-Powered Contextual Website Chatbot with Memory (EduMind RAG SaaS)**.

---

## 1. Overview & Objectives

Phase 2 builds the core data ingestion pipeline:
- **Multi-Format Text Extraction**: Extract clean text from PDF, DOCX, TXT, and FAQ CSV documents.
- **Text Preprocessing & Chunking**: Apply sliding window token/word chunking (500-word chunk size, 100-word chunk overlap) to optimize retrieval performance.
- **Embedding Generation**: Convert text chunks into 384-dimensional dense vectors using HuggingFace `sentence-transformers/all-MiniLM-L6-v2`.
- **Vector Upsert & Database Record**: Batch upsert vectors into Pinecone with enriched metadata (document ID, filename, page, chunk index) and record metadata in Supabase.

---

## 2. Text Extraction Module (`backend/upload.py`)

Create `backend/upload.py` to extract raw text from supported file formats:

```python
import os
import io
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

class DocumentExtractor:
    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        pdf = PdfReader(io.BytesIO(file_bytes))
        extracted_text = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                extracted_text.append(f"--- Page {i + 1} ---\n" + text)
        return "\n\n".join(extracted_text)

    @staticmethod
    def extract_from_docx(file_bytes: bytes) -> str:
        doc = DocxDocument(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    @staticmethod
    def extract_from_txt(file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8", errors="ignore")

    @staticmethod
    def extract_from_csv_faq(file_bytes: bytes) -> list:
        """
        Parses CSV containing 'question' and 'answer' columns.
        Returns a list of formatted Q&A text blocks.
        """
        df = pd.read_csv(io.BytesIO(file_bytes))
        if "question" not in df.columns or "answer" not in df.columns:
            raise ValueError("CSV FAQ file must contain 'question' and 'answer' columns.")
        
        faq_items = []
        for _, row in df.iterrows():
            faq_text = f"Question: {row['question']}\nAnswer: {row['answer']}"
            faq_items.append(faq_text)
        return faq_items

    @classmethod
    def extract_text(cls, file_bytes: bytes, filename: str) -> str:
        ext = filename.split(".")[-1].lower()
        if ext == "pdf":
            return cls.extract_from_pdf(file_bytes)
        elif ext == "docx":
            return cls.extract_from_docx(file_bytes)
        elif ext == "txt":
            return cls.extract_from_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported file extension: .{ext}")
```

---

## 3. Text Preprocessing & Chunking Engine (`backend/utils/text_splitter.py`)

Create `backend/utils/text_splitter.py` for chunking text according to PRD specs:

```python
import re

class SlidingWindowChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        # Normalize whitespace and strip special non-printable characters
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def split_text(self, text: str) -> list:
        """
        Splits text into chunks of 500 words with 100-word overlap.
        """
        cleaned = self.clean_text(text)
        words = cleaned.split(" ")
        
        if len(words) <= self.chunk_size:
            return [" ".join(words)]
        
        chunks = []
        step = self.chunk_size - self.chunk_overlap
        
        for i in range(0, len(words), step):
            chunk_words = words[i : i + self.chunk_size]
            chunk_str = " ".join(chunk_words)
            if len(chunk_words) >= 20:  # Ignore tiny leftover tail chunks
                chunks.append(chunk_str)
            if i + self.chunk_size >= len(words):
                break
                
        return chunks

# Default chunker instance
chunker = SlidingWindowChunker(chunk_size=500, chunk_overlap=100)
```

---

## 4. Embedding Generation Service (`backend/embeddings.py`)

Create `backend/embeddings.py` to generate embeddings using Hugging Face Sentence Transformers:

```python
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

class EmbeddingEngine:
    def __init__(self):
        print(f"Loading embedding model '{MODEL_NAME}'...")
        self.model = SentenceTransformer(MODEL_NAME)
        print("Embedding model loaded successfully.")

    def generate_embedding(self, text: str) -> list:
        """
        Generates a 384-dim dense float vector for a single string.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_batch_embeddings(self, texts: list) -> list:
        """
        Generates embeddings for a batch of strings.
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=32)
        return [emb.tolist() for emb in embeddings]

# Singleton embedding engine
embedding_engine = EmbeddingEngine()
```

---

## 5. Ingestion Orchestrator (`backend/ingestion_service.py`)

Create `backend/ingestion_service.py` combining extract, chunk, embed, and store logic:

```python
import uuid
from backend.upload import DocumentExtractor
from backend.utils.text_splitter import chunker
from backend.embeddings import embedding_engine
from backend.pinecone_db import pinecone_client
from backend.database import record_document

def process_and_ingest_document(file_bytes: bytes, filename: str, uploaded_by: str = None) -> dict:
    # 1. Extract Text
    raw_text = DocumentExtractor.extract_text(file_bytes, filename)
    if not raw_text or not raw_text.strip():
        raise ValueError("Document contains no readable text.")

    # 2. Chunk Text
    chunks = chunker.split_text(raw_text)
    chunk_count = len(chunks)

    # 3. Save Document Record in Supabase
    doc_record = record_document(
        title=filename,
        file_name=filename,
        file_type=filename.split(".")[-1].lower(),
        file_size=len(file_bytes),
        chunk_count=chunk_count,
        uploaded_by=uploaded_by
    )
    document_id = doc_record["id"]

    # 4. Generate Embeddings for Chunks
    embeddings = embedding_engine.generate_batch_embeddings(chunks)

    # 5. Build Pinecone Vector Payloads
    vectors_to_upsert = []
    for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        vector_id = f"{document_id}#chunk-{idx}"
        metadata = {
            "document_id": str(document_id),
            "file_name": filename,
            "chunk_index": idx,
            "text": chunk_text
        }
        vectors_to_upsert.append((vector_id, embedding, metadata))

    # 6. Batch Upsert to Pinecone
    pinecone_client.upsert_vectors(vectors_to_upsert)

    return {
        "status": "success",
        "document_id": document_id,
        "file_name": filename,
        "total_chunks": chunk_count
    }
```

---

## 6. Verification Checklist

- [ ] Executed test document extraction script with `.pdf`, `.docx`, `.txt`, and FAQ `.csv`.
- [ ] Confirmed sliding window chunker splits 1200-word text into overlapping 500-word chunks.
- [ ] Verified `embedding_engine.generate_embedding("test query")` returns a 384-length float array.
- [ ] Verified end-to-end ingestion pipeline upserts vectors into Pinecone index and updates `documents` table in Supabase.
