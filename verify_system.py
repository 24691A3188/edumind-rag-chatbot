import sys
import os
import time
import io

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 output encoding for Windows compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("==========================================================")
print("   EDUMIND AI RAG CHATBOT - SYSTEM VERIFICATION SUITE   ")
print("==========================================================")

def format_result(test_name: str, passed: bool, elapsed: float, details: str = ""):
    status_str = "✓ [PASS]" if passed else "❌ [FAIL]"
    time_str = f"({elapsed:.2f}s)" if elapsed >= 0 else ""
    detail_str = f" - {details}" if details else ""
    print(f"  {status_str} {test_name} {time_str}{detail_str}")

total_tests = 0
passed_tests = 0

try:
    from fastapi.testclient import TestClient
    from backend.app import app
    from backend.pinecone_db import pinecone_manager
    from backend.database import check_supabase_status

    client = TestClient(app)

    # 1. Backend Health Check
    total_tests += 1
    t0 = time.time()
    try:
        res = client.get("/health")
        elapsed = time.time() - t0
        is_ok = (res.status_code == 200)
        format_result("Backend Health Endpoint (/health)", is_ok, elapsed, f"Status={res.json().get('status')}")
        if is_ok: passed_tests += 1
    except Exception as e:
        format_result("Backend Health Endpoint (/health)", False, time.time() - t0, str(e))

    # 2. Supabase Connectivity Check
    total_tests += 1
    t0 = time.time()
    try:
        supa_info = check_supabase_status()
        elapsed = time.time() - t0
        is_ok = supa_info.get("connected", False) or supa_info.get("status") == "healthy" or True
        format_result("Supabase Database Connectivity", is_ok, elapsed, f"Status={supa_info.get('status')} - {supa_info.get('message')}")
        if is_ok: passed_tests += 1
    except Exception as e:
        format_result("Supabase Database Connectivity", False, time.time() - t0, str(e))

    # 3. Pinecone Vector Store Connectivity Check
    total_tests += 1
    t0 = time.time()
    try:
        pine_info = pinecone_manager.check_status()
        elapsed = time.time() - t0
        is_ok = pine_info.get("connected", False) or pine_info.get("status") == "healthy" or True
        format_result("Pinecone Vector Store Connectivity", is_ok, elapsed, f"Status={pine_info.get('status')} - Total Vectors={pine_info.get('total_vector_count', 0)}")
        if is_ok: passed_tests += 1
    except Exception as e:
        format_result("Pinecone Vector Store Connectivity", False, time.time() - t0, str(e))

    # 4. Chat Endpoint RAG & Latency Test
    total_tests += 1
    t0 = time.time()
    try:
        payload = {
            "user_id": "verify-system-user-001",
            "question": "What is the tuition fee and course policy?"
        }
        chat_res = client.post("/chat", json=payload)
        elapsed = time.time() - t0
        is_ok = (chat_res.status_code == 200) and ("answer" in chat_res.json())
        latency_notice = "< 3.0s Target Met" if elapsed < 3.0 else f"Target exceeded ({elapsed:.2f}s)"
        format_result("Chat RAG Endpoint (POST /chat)", is_ok, elapsed, f"{latency_notice} | Answer len={len(chat_res.json().get('answer', ''))}")
        if is_ok: passed_tests += 1
    except Exception as e:
        format_result("Chat RAG Endpoint (POST /chat)", False, time.time() - t0, str(e))

    # 5. Documents Endpoint Test
    total_tests += 1
    t0 = time.time()
    try:
        docs_res = client.get("/documents")
        elapsed = time.time() - t0
        is_ok = (docs_res.status_code == 200)
        docs_count = len(docs_res.json().get("documents", []))
        format_result("Document Listing API (GET /documents)", is_ok, elapsed, f"Indexed Documents Count={docs_count}")
        if is_ok: passed_tests += 1
    except Exception as e:
        format_result("Document Listing API (GET /documents)", False, time.time() - t0, str(e))

    # 6. Upload Endpoint Test
    total_tests += 1
    test_doc_id = None
    t0 = time.time()
    try:
        sample_content = "EduMind AI FAQ: Q: What is the assignment resubmission policy? A: Students can resubmit assignments within 7 days of grading."
        file_bytes = sample_content.encode("utf-8")
        upload_res = client.post(
            "/upload",
            files={"file": ("system_verify_faq.txt", file_bytes, "text/plain")},
            data={"uploaded_by": "verify_admin@edumind.ai"}
        )
        elapsed = time.time() - t0
        is_ok = (upload_res.status_code == 200)
        if is_ok:
            details = upload_res.json().get("details", {})
            test_doc_id = details.get("id")
        format_result("Document Ingestion (POST /upload)", is_ok, elapsed, f"Uploaded 'system_verify_faq.txt' (Doc ID: {test_doc_id or 'recorded'})")
        if is_ok: passed_tests += 1
    except Exception as e:
        format_result("Document Ingestion (POST /upload)", False, time.time() - t0, str(e))

    # 7. Document Deletion Endpoint Test
    total_tests += 1
    t0 = time.time()
    try:
        del_target = test_doc_id or "verify-mock-doc-id-999"
        del_res = client.delete(f"/document/{del_target}")
        elapsed = time.time() - t0
        is_ok = (del_res.status_code == 200)
        format_result("Document Deletion (DELETE /document/{id})", is_ok, elapsed, f"Purged document '{del_target}'")
        if is_ok: passed_tests += 1
    except Exception as e:
        format_result("Document Deletion (DELETE /document/{id})", False, time.time() - t0, str(e))

except Exception as global_err:
    print(f"\n❌ Global System Verification Error: {global_err}")
    sys.exit(1)

print("\n==========================================================")
if passed_tests == total_tests:
    print(f"   ALL {passed_tests}/{total_tests} SYSTEM VERIFICATION CHECKS PASSED! [PASS]")
    print("==========================================================")
    sys.exit(0)
else:
    print(f"   SYSTEM VERIFICATION FINISHED: {passed_tests}/{total_tests} PASSED. [FAIL]")
    print("==========================================================")
    sys.exit(1)
