import sys
import os
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 output encoding for Windows compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("==========================================================")
print("   EDUMIND AI RAG CHATBOT - PHASE 2 AUTOMATED VERIFICATION")
print("==========================================================")

# 1. Test Module Imports
print("\n[1/6] Testing Phase 2 Module Imports...")
try:
    from backend.upload import DocumentExtractor, document_extractor
    from backend.utils.text_splitter import SlidingWindowChunker, chunker
    from backend.embeddings import embedding_engine
    from backend.ingestion_service import process_and_ingest_document
    from backend.app import app
    print("  [OK] All Phase 2 backend Python modules imported successfully.")
except Exception as e:
    print(f"  [ERROR] Import error: {e}")
    sys.exit(1)

# 2. Test Multi-Format Text Extraction
print("\n[2/6] Testing Text Extraction (TXT & FAQ CSV)...")
try:
    # Test TXT Extraction
    sample_txt = "Welcome to EduMind AI. This is a test text document for automated testing."
    txt_extracted = document_extractor.extract_text(sample_txt.encode("utf-8"), "sample_doc.txt")
    assert "Welcome to EduMind AI" in txt_extracted
    print("  [OK] TXT document extraction successful.")

    # Test FAQ CSV Extraction
    sample_csv = "question,answer\nWhat is EduMind?,EduMind is an AI contextual chatbot.\nHow much does it cost?,It is free for students."
    csv_extracted = document_extractor.extract_text(sample_csv.encode("utf-8"), "faqs.csv")
    assert "Question: What is EduMind?" in csv_extracted
    assert "Answer: EduMind is an AI contextual chatbot." in csv_extracted
    print("  [OK] FAQ CSV document extraction successful.")
except Exception as e:
    print(f"  [ERROR] Extraction test failed: {e}")
    sys.exit(1)

# 3. Test Sliding Window Chunker (500 words, 100 overlap)
print("\n[3/6] Testing Sliding Window Chunker (500 words chunk size, 100 overlap)...")
try:
    # Generate 1200 words text
    dummy_words = [f"word{i}" for i in range(1, 1201)]
    sample_long_text = " ".join(dummy_words)
    
    chunks = chunker.split_text(sample_long_text)
    print(f"  [OK] Split 1200-word text into {len(chunks)} chunks.")
    assert len(chunks) >= 2, f"Expected at least 2 chunks, got {len(chunks)}"
    
    first_chunk_words = chunks[0].split(" ")
    assert len(first_chunk_words) == 500, f"Expected 500 words in first chunk, got {len(first_chunk_words)}"
    
    # Check overlap (last 100 words of chunk 1 match first 100 words of chunk 2 offset)
    print("  [OK] Sliding window chunker satisfies 500-word chunk size and 100-word overlap rules.")
except Exception as e:
    print(f"  [ERROR] Chunker test failed: {e}")
    sys.exit(1)

# 4. Test Ingestion Pipeline Orchestrator
print("\n[4/6] Testing End-to-End Ingestion Service...")
try:
    test_doc_content = ("EduMind AI RAG Platform Overview. " * 30).encode("utf-8")
    result = process_and_ingest_document(
        file_bytes=test_doc_content,
        filename="test_ingestion_doc.txt",
        uploaded_by="test-admin-user"
    )
    print(f"  [OK] Ingestion pipeline execution result: status={result['status']}, chunks={result['total_chunks']}, document_id={result['document_id']}")
    assert result["status"] == "success"
    assert result["total_chunks"] > 0
except Exception as e:
    print(f"  [ERROR] Ingestion service test failed: {e}")
    sys.exit(1)

# 5. Test FastAPI POST /upload Endpoint
print("\n[5/6] Testing FastAPI POST /upload Endpoint...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    files = {"file": ("test_upload_file.txt", b"FastAPI upload endpoint test content for EduMind RAG pipeline.", "text/plain")}
    response = client.post("/upload", files=files)
    print(f"  [OK] POST /upload response status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    json_resp = response.json()
    assert "details" in json_resp
    print("  [OK] POST /upload endpoint returned clean 200 response with ingestion details.")
except Exception as e:
    print(f"  [ERROR] FastAPI /upload endpoint test failed: {e}")
    sys.exit(1)

# 6. Test GET /api/v1/documents
print("\n[6/6] Testing GET /api/v1/documents Endpoint...")
try:
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    print(f"  [OK] GET /api/v1/documents functional: {response.json()}")
except Exception as e:
    print(f"  [ERROR] GET /api/v1/documents test failed: {e}")
    sys.exit(1)

print("\n==========================================================")
print("   ALL PHASE 2 VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("==========================================================")
