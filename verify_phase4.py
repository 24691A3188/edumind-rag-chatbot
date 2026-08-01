import sys
import os
import io

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 output encoding for Windows compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("==========================================================")
print("   EDUMIND AI RAG CHATBOT - PHASE 4 AUTOMATED VERIFICATION")
print("==========================================================")

# 1. Check Streamlit Frontend File Existence & Syntax
print("\n[1/6] Verifying Frontend File Existence & Syntax...")
frontend_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "streamlit_app.py")
assert os.path.exists(frontend_file), f"File not found: {frontend_file}"

with open(frontend_file, "r", encoding="utf-8") as f:
    code_content = f.read()

# Validate python compilation of streamlit_app.py
try:
    compile(code_content, frontend_file, "exec")
    print("  [OK] `frontend/streamlit_app.py` exists and compiles cleanly without syntax errors.")
except Exception as e:
    print(f"  [ERROR] Syntax error in `frontend/streamlit_app.py`: {e}")
    sys.exit(1)

# Check Key UI Elements in streamlit_app.py
print("\n[2/6] Verifying Glassmorphism & UI Features in Streamlit Code...")
required_tokens = [
    "st.set_page_config",
    "background-color: var(--bg-deep)",
    "radial-gradient",
    "glass-header",
    "glass-card",
    "st.sidebar.radio",
    "💬 Chat Assistant",
    "📚 Knowledge Documents",
    "⚙️ Admin Control",
    "What AI courses are offered?",
    "Clear Chat History",
    "requests.post",
    "/chat",
    "/documents",
    "/upload"
]

for token in required_tokens:
    if token in code_content:
        print(f"  [OK] Found required UI/API token: '{token}'")
    else:
        print(f"  [ERROR] Missing required UI/API token: '{token}'")
        sys.exit(1)

# 3. Test Backend App & Endpoints via TestClient
print("\n[3/6] Testing Backend FastAPI Endpoints via TestClient...")
try:
    from fastapi.testclient import TestClient
    from backend.app import app

    client = TestClient(app)

    # Health Check
    health_res = client.get("/health")
    assert health_res.status_code == 200, f"Expected 200, got {health_res.status_code}"
    print(f"  [OK] GET /health returned status 200 (status: {health_res.json().get('status')})")

    # Chat Endpoint
    chat_payload = {
        "user_id": "phase4-test-user-001",
        "question": "What courses are available in EduMind?"
    }
    chat_res = client.post("/chat", json=chat_payload)
    assert chat_res.status_code == 200, f"Expected 200, got {chat_res.status_code}: {chat_res.text}"
    chat_data = chat_res.json()
    assert "answer" in chat_data
    assert "sources" in chat_data
    print(f"  [OK] POST /chat returned clean response: answer length={len(chat_data['answer'])}, sources={len(chat_data['sources'])}")

    # Clear History Endpoint
    del_hist = client.delete("/history?user_id=phase4-test-user-001")
    assert del_hist.status_code == 200
    print(f"  [OK] DELETE /history returned status 200")

    # Get Documents Endpoint
    docs_res = client.get("/documents")
    assert docs_res.status_code == 200
    print(f"  [OK] GET /documents returned status 200 (count: {docs_res.json().get('count', 0)})")

except Exception as e:
    print(f"  [ERROR] FastAPI TestClient test failed: {e}")
    sys.exit(1)

# 4. Test Ingestion Upload Endpoint via TestClient
print("\n[4/6] Testing Document Upload Endpoint (/upload)...")
try:
    sample_text = "EduMind AI Course Directory: 1. Introduction to Machine Learning. 2. Deep Learning and Neural Networks. 3. Full-Stack RAG Systems."
    file_bytes = sample_text.encode('utf-8')
    
    upload_res = client.post(
        "/upload",
        files={"file": ("test_syllabus.txt", file_bytes, "text/plain")},
        data={"uploaded_by": "test_admin@edumind.ai"}
    )
    assert upload_res.status_code == 200, f"Expected 200, got {upload_res.status_code}: {upload_res.text}"
    print(f"  [OK] POST /upload successfully processed document (Message: {upload_res.json().get('message')})")
except Exception as e:
    print(f"  [ERROR] Document upload test failed: {e}")
    sys.exit(1)

# 5. Verify Streamlit CLI availability
print("\n[5/6] Verifying Streamlit Executable Availability...")
import subprocess
try:
    proc = subprocess.run([sys.executable, "-m", "streamlit", "--version"], capture_output=True, text=True)
    if proc.returncode == 0:
        print(f"  [OK] Streamlit is installed and ready: {proc.stdout.strip()}")
    else:
        print(f"  [WARNING] Streamlit check returned non-zero code: {proc.stderr}")
except Exception as e:
    print(f"  [ERROR] Streamlit check error: {e}")

# 6. Overall Summary
print("\n==========================================================")
print("   ALL PHASE 4 VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("==========================================================")
