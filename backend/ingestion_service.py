import logging
import uuid
from typing import Dict, Any, Optional
from backend.upload import DocumentExtractor
from backend.utils.text_splitter import chunker
from backend.embeddings import embedding_engine
from backend.pinecone_db import pinecone_manager
from backend.database import record_document

logger = logging.getLogger("edumind.ingestion")

def process_and_ingest_document(file_bytes: bytes, filename: str, uploaded_by: Optional[str] = None) -> Dict[str, Any]:
    """
    End-to-End Document Ingestion Pipeline:
    1. Multi-format text extraction (PDF, DOCX, TXT, CSV)
    2. Text cleaning & sliding window chunking (500 words, 100 word overlap)
    3. Document metadata record created in Supabase
    4. 384-dim dense embedding generation via SentenceTransformers
    5. Batch vector payload construction & upsert into Pinecone
    """
    logger.info(f"Starting ingestion pipeline for file '{filename}' ({len(file_bytes)} bytes)...")

    # 1. Extract Text
    raw_text = DocumentExtractor.extract_text(file_bytes=file_bytes, filename=filename)
    
    # 2. Preprocess & Chunk Text
    chunks = chunker.split_text(raw_text)
    chunk_count = len(chunks)
    logger.info(f"Document '{filename}' split into {chunk_count} chunks.")

    # 3. Create Document Record in Supabase
    file_type = filename.split(".")[-1].lower() if "." in filename else "unknown"
    doc_record = record_document(
        title=filename,
        file_name=filename,
        file_type=file_type,
        file_size=len(file_bytes),
        chunk_count=chunk_count,
        uploaded_by=uploaded_by
    )
    document_id = str(doc_record.get("id", uuid.uuid4()))

    # 4. Generate Vector Embeddings
    logger.info(f"Generating embeddings for {chunk_count} text chunks...")
    embeddings = embedding_engine.generate_batch_embeddings(chunks)

    # 5. Build Vector Payloads for Pinecone
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

    # 6. Batch Upsert to Pinecone Vector Store
    logger.info(f"Upserting {len(vectors_to_upsert)} vectors to Pinecone...")
    upsert_success = pinecone_manager.upsert_vectors(vectors_to_upsert)

    return {
        "status": "success",
        "id": document_id,
        "document_id": document_id,
        "file_name": filename,
        "file_type": file_type,
        "file_size_bytes": len(file_bytes),
        "total_chunks": chunk_count,
        "vectors_upserted": len(vectors_to_upsert),
        "vector_store_synced": upsert_success
    }
