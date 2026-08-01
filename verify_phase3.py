import sys
import os
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 output encoding for Windows compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("==========================================================")
print("   EDUMIND AI RAG CHATBOT - PHASE 3 AUTOMATED VERIFICATION")
print("==========================================================")

# 1. Test Imports
print("\n[1/7] Testing Phase 3 Module Imports...")
try:
    from backend.memory import ConversationMemoryManager, memory_manager
    from backend.rag import RAGEngine, rag_engine
    from backend.app import app
    print("  [OK] All Phase 3 backend Python modules imported successfully.")
except Exception as e:
    print(f"  [ERROR] Import error: {e}")
    sys.exit(1)

# 2. Test Conversation Memory Manager
print("\n[2/7] Testing Conversation Memory Manager...")
try:
    formatted_mem = memory_manager.get_formatted_memory(user_id="test-memory-user-123", limit=5)
    assert isinstance(formatted_mem, str)
    print(f"  [OK] Memory manager returned formatted string (length={len(formatted_mem)}).")
except Exception as e:
    print(f"  [ERROR] Memory manager test failed: {e}")
    sys.exit(1)

# 3. Test RAG Engine Execution
print("\n[3/7] Testing RAG Engine (Retrieval + Prompt Assembly + Response)...")
try:
    rag_res = rag_engine.generate_response(
        user_id="test-phase3-user",
        query="What is the tuition fee and course schedule?"
    )
    print("  [OK] RAG engine execution output:")
    print(f"    - Answer snippet: {rag_res['answer'][:120]}...")
    print(f"    - Chunks retrieved: {rag_res['chunks_retrieved']}")
    print(f"    - Sources count: {len(rag_res['sources'])}")
    assert "answer" in rag_res
    assert "sources" in rag_res
    assert "chunks_retrieved" in rag_res
except Exception as e:
    print(f"  [ERROR] RAG Engine test failed: {e}")
    sys.exit(1)

# 4. Test FastAPI POST /chat Endpoint
print("\n[4/7] Testing FastAPI POST /chat Endpoint...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)

    chat_payload = {
        "user_id": "test-phase3-user",
        "question": "What is the policy for submitting assignments?"
    }
    chat_res = client.post("/chat", json=chat_payload)
    print(f"  [OK] POST /chat status code: {chat_res.status_code}")
    assert chat_res.status_code == 200, f"Expected 200, got {chat_res.status_code}: {chat_res.text}"
    chat_json = chat_res.json()
    assert "answer" in chat_json
    assert "sources" in chat_json
    print(f"  [OK] POST /chat returned clean 200 response with answer.")
except Exception as e:
    print(f"  [ERROR] POST /chat endpoint test failed: {e}")
    sys.exit(1)

# 5. Test FastAPI GET & DELETE /history Endpoints
print("\n[5/7] Testing FastAPI Chat History Endpoints (GET & DELETE /history)...")
try:
    # Test GET /history
    get_hist_res = client.get("/history?user_id=test-phase3-user")
    print(f"  [OK] GET /history status code: {get_hist_res.status_code}")
    assert get_hist_res.status_code == 200
    hist_json = get_hist_res.json()
    assert hist_json["status"] == "success"
    print(f"  [OK] GET /history returned history records count: {hist_json.get('count', 0)}")

    # Test DELETE /history
    del_hist_res = client.delete("/history?user_id=test-phase3-user")
    print(f"  [OK] DELETE /history status code: {del_hist_res.status_code}")
    assert del_hist_res.status_code == 200
    print("  [OK] DELETE /history endpoint executed successfully.")
except Exception as e:
    print(f"  [ERROR] History endpoints test failed: {e}")
    sys.exit(1)

# 6. Test FastAPI Document Endpoints (GET /documents & DELETE /document/{id})
print("\n[6/7] Testing Document Management Endpoints...")
try:
    get_docs_res = client.get("/documents")
    assert get_docs_res.status_code == 200
    print(f"  [OK] GET /documents status code: 200")

    del_doc_res = client.delete("/document/mock-test-doc-id-999")
    assert del_doc_res.status_code == 200
    print(f"  [OK] DELETE /document/mock-test-doc-id-999 status code: 200")
except Exception as e:
    print(f"  [ERROR] Document management endpoints test failed: {e}")
    sys.exit(1)

# 7. Test Root & Docs Swagger Endpoint
print("\n[7/7] Testing Swagger OpenAPI Documentation Endpoint (/docs)...")
try:
    docs_res = client.get("/docs")
    assert docs_res.status_code == 200
    print("  [OK] Swagger UI OpenAPI documentation (/docs) is accessible and loads cleanly.")
except Exception as e:
    print(f"  [ERROR] Swagger UI test failed: {e}")
    sys.exit(1)

print("\n==========================================================")
print("   ALL PHASE 3 VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("==========================================================")
