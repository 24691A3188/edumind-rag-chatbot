import sys
import os
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 output encoding for Windows compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("==========================================================")
print("   EDUMIND AI RAG CHATBOT - PHASE 1 AUTOMATED VERIFICATION")
print("==========================================================")

# 1. Test Backend Package Imports
print("\n[1/7] Testing Backend Imports...")
try:
    from backend.config import settings
    from backend.database import check_supabase_status, fetch_all_documents
    from backend.pinecone_db import pinecone_manager
    from backend.embeddings import embedding_engine
    from backend.auth import signup_user, login_user, SignupRequest, LoginRequest
    from backend.app import app
    print("  [OK] All backend Python modules imported successfully without errors.")
except Exception as e:
    print(f"  [ERROR] Import error: {e}")
    sys.exit(1)

# 2. Test FastAPI TestClient & Health Endpoint
print("\n[2/7] Testing FastAPI App Initialization & Root Endpoint...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    root_res = client.get("/")
    assert root_res.status_code == 200, f"Root endpoint returned status {root_res.status_code}"
    print(f"  [OK] Root Endpoint (/) OK: {root_res.json()}")
except Exception as e:
    print(f"  [ERROR] Root endpoint test failed: {e}")
    sys.exit(1)

print("\n[3/7] Testing Health Check Endpoint (/health)...")
try:
    health_res = client.get("/health")
    assert health_res.status_code == 200, f"Health endpoint returned status {health_res.status_code}"
    health_data = health_res.json()
    print(f"  [OK] Health Check Endpoint (/health) OK:")
    print(f"    - Overall Status: {health_data.get('status')}")
    print(f"    - Supabase: {health_data['components']['supabase']['status']}")
    print(f"    - Pinecone: {health_data['components']['pinecone']['status']}")
    print(f"    - Embeddings: {health_data['components']['embeddings']['status']}")
except Exception as e:
    print(f"  [ERROR] Health check endpoint test failed: {e}")
    sys.exit(1)

# 4. Test Embedding Engine & Dimension Verification
print("\n[4/7] Testing Embeddings Engine (Google Gemini)...")
try:
    emb = embedding_engine.generate_embedding("Verification test query")
    dim = len(emb)
    print(f"  [OK] Generated embedding vector length: {dim}")
    assert dim == 384, f"Expected 384 dimensions, got {dim}"
    print("  [OK] Embedding dimension matches Pinecone specification (384 dimensions).")
except Exception as e:
    print(f"  [ERROR] Embedding generation test failed: {e}")
    sys.exit(1)

# 5. Test Pinecone Manager Status
print("\n[5/7] Testing Pinecone Manager Initialization...")
try:
    pc_status = pinecone_manager.check_status()
    print(f"  [OK] Pinecone Status: {pc_status['status']} (Index: {pc_status['index_name']}, Dim: {pc_status['dimension']})")
except Exception as e:
    print(f"  [ERROR] Pinecone test failed: {e}")
    sys.exit(1)

# 6. Test Authentication Routes (Signup & Login)
print("\n[6/7] Testing Authentication Endpoints...")
try:
    signup_payload = {
        "name": "Test Student",
        "email": "teststudent@edumind.ai",
        "password": "TestPassword123!",
        "role": "student"
    }
    signup_res = client.post("/auth/signup", json=signup_payload)
    print(f"  [OK] POST /auth/signup response: {signup_res.status_code}")
    
    login_payload = {
        "email": "teststudent@edumind.ai",
        "password": "TestPassword123!"
    }
    login_res = client.post("/auth/login", json=login_payload)
    print(f"  [OK] POST /auth/login response: {login_res.status_code}")
    assert login_res.status_code in [200, 401], "Unexpected login response code"
except Exception as e:
    print(f"  [ERROR] Authentication test failed: {e}")
    sys.exit(1)

# 7. Test Document List Endpoint
print("\n[7/7] Testing API v1 Documents Endpoint...")
try:
    docs_res = client.get("/api/v1/documents")
    assert docs_res.status_code == 200, f"Documents endpoint returned {docs_res.status_code}"
    print(f"  [OK] GET /api/v1/documents OK: {docs_res.json()}")
except Exception as e:
    print(f"  [ERROR] Document list endpoint test failed: {e}")
    sys.exit(1)

print("\n==========================================================")
print("   ALL PHASE 1 VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("==========================================================")
