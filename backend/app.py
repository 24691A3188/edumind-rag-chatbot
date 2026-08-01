import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import settings
from backend.database import check_supabase_status, fetch_all_documents, delete_document_record, fetch_chat_history, clear_chat_history_record, supabase_client
from backend.pinecone_db import pinecone_manager
from backend.embeddings import embedding_engine
from backend.auth import SignupRequest, LoginRequest, signup_user, login_user
from backend.ingestion_service import process_and_ingest_document
from backend.rag import rag_engine

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("edumind.app")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Backend for EduMind AI Contextual Website Chatbot with Memory (Phases 1-5 Complete)",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class SourceItem(BaseModel):
    file_name: str
    score: float
    chunk: str

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier", json_schema_extra={"example": "user-123"})
    question: str = Field(..., min_length=1, description="Question for the AI chatbot", json_schema_extra={"example": "What AI courses are offered?"})

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    chunks_retrieved: int

# System Endpoints
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/", tags=["Root"])
def read_root() -> Dict[str, Any]:
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_url": "/health"
    }

@app.get("/health", tags=["Health & Status"])
def health_check() -> Dict[str, Any]:
    supabase_info = check_supabase_status()
    pinecone_info = pinecone_manager.check_status()
    embedding_info = embedding_engine.check_status()

    is_overall_healthy = (
        supabase_info.get("connected", False) or settings.is_supabase_configured() == False
    ) and (
        pinecone_info.get("connected", False) or settings.is_pinecone_configured() == False
    )

    return {
        "status": "healthy" if is_overall_healthy else "degraded",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "components": {
            "supabase": supabase_info,
            "pinecone": pinecone_info,
            "embeddings": embedding_info
        }
    }

# Auth Routes
@app.post("/auth/signup", tags=["Authentication"])
def signup(request: SignupRequest) -> Dict[str, Any]:
    try:
        return signup_user(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration server error: {str(e)}")

@app.post("/auth/login", tags=["Authentication"])
def login(request: LoginRequest) -> Dict[str, Any]:
    try:
        return login_user(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login server error: {str(e)}")

# RAG & Chat Routes
@app.post("/chat", response_model=ChatResponse, tags=["RAG Chat"])
def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """
    RAG Chat endpoint: Accepts user_id and question, performs vector retrieval,
    injects memory, calls LLM, records interaction in Supabase, and returns grounded answer with sources.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        response_data = rag_engine.generate_response(
            user_id=request.user_id,
            query=request.question.strip()
        )
        return response_data
    except Exception as e:
        logger.error(f"Chat generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")

@app.get("/history", tags=["Chat History"])
def get_chat_history_endpoint(user_id: str = Query(..., description="User ID to retrieve history for")) -> Dict[str, Any]:
    """
    Retrieves previous conversation turns for the specified user_id.
    """
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="User ID parameter is required.")
        
    history = fetch_chat_history(user_id=user_id, limit=20)
    return {"status": "success", "user_id": user_id, "count": len(history), "history": history}

@app.delete("/history", tags=["Chat History"])
def clear_chat_history_endpoint(user_id: str = Query(..., description="User ID to clear history for")) -> Dict[str, Any]:
    """
    Clears all chat history entries for the specified user_id.
    """
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="User ID parameter is required.")
        
    clear_chat_history_record(user_id=user_id)
    return {"status": "success", "message": f"Chat history for user '{user_id}' cleared successfully."}

# Admin & Vector Store Analytics Routes
@app.get("/admin/stats", tags=["Admin & Vector Analytics"])
@app.get("/api/v1/admin/stats", tags=["Admin & Vector Analytics"])
def get_admin_stats() -> Dict[str, Any]:
    """
    Returns vector index metrics, vector count, dimension, and connectivity status.
    """
    return pinecone_manager.get_index_stats()

# Document Ingestion & Management Routes
@app.post("/upload", tags=["Document Management"])
async def upload_document(
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Ingests PDF, DOCX, TXT, or FAQ CSV document into the RAG vector knowledge base.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    filename = file.filename.strip()
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    supported_extensions = ["pdf", "docx", "txt", "csv"]

    if ext not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{ext}'. Supported formats: {', '.join(supported_extensions)}"
        )

    try:
        contents = await file.read()
        if not contents or len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

        result = process_and_ingest_document(
            file_bytes=contents,
            filename=filename,
            uploaded_by=uploaded_by
        )
        return {"message": f"Document '{filename}' successfully processed and indexed.", "details": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing upload '{filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@app.get("/documents", tags=["Document Management"])
@app.get("/api/v1/documents", tags=["Document Management"])
def list_documents() -> Dict[str, Any]:
    """
    Lists all indexed documents recorded in the database.
    """
    docs = fetch_all_documents()
    return {"status": "success", "count": len(docs), "documents": docs}

@app.delete("/document/{document_id}", tags=["Document Management"])
def delete_document(document_id: str) -> Dict[str, Any]:
    """
    Purges document metadata from Supabase and associated vector embeddings from Pinecone.
    Prevents orphan vectors.
    """
    if not document_id or not document_id.strip():
        raise HTTPException(status_code=400, detail="Invalid document ID.")

    try:
        # Delete vectors in Pinecone
        pinecone_manager.delete_by_document(document_id)
        # Delete record in Supabase
        delete_document_record(document_id)
        return {"message": f"Document '{document_id}' and associated vectors deleted successfully."}
    except Exception as e:
        logger.error(f"Error deleting document '{document_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Document deletion failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import socket

    def find_available_port(start_port: int, host: str = "127.0.0.1") -> int:
        for p in range(start_port, start_port + 10):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind((host, p))
                    return p
                except OSError:
                    continue
        return start_port

    target_port = find_available_port(settings.PORT, settings.HOST)
    if target_port != settings.PORT:
        logger.info(f"Port {settings.PORT} is busy, auto-switching to available port {target_port}")
    
    uvicorn.run("backend.app:app", host=settings.HOST, port=target_port, reload=True)
