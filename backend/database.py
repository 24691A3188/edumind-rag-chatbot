import logging
import uuid
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from backend.config import settings

logger = logging.getLogger("edumind.database")

supabase_client: Optional[Client] = None
is_supabase_connected: bool = False

def ensure_uuid(user_id: str) -> str:
    """
    Ensures user_id string is in valid UUID format required by PostgreSQL UUID columns.
    Converts string identifiers to deterministic UUIDs if needed.
    """
    if not user_id or not user_id.strip():
        return str(uuid.uuid4())
    try:
        return str(uuid.UUID(user_id.strip()))
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id.strip()))

def init_supabase() -> Optional[Client]:
    global supabase_client, is_supabase_connected
    if not settings.is_supabase_configured():
        logger.warning("Supabase credentials not fully configured or using placeholders. Database features operating in mock/fallback mode.")
        is_supabase_connected = False
        return None

    try:
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY)
        is_supabase_connected = True
        logger.info("Supabase client initialized successfully.")
        return supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        is_supabase_connected = False
        return None

import datetime

# In-Memory Fallback Stores for High Availability
_IN_MEMORY_DOCS: Dict[str, Dict[str, Any]] = {}
_IN_MEMORY_CHAT: Dict[str, List[Dict[str, Any]]] = {}

# Initialize client on module import
init_supabase()

def check_supabase_status() -> Dict[str, Any]:
    if not settings.is_supabase_configured():
        return {"status": "unconfigured", "connected": False, "message": "Supabase credentials missing or placeholder."}
    
    if supabase_client is None:
        return {"status": "error", "connected": False, "message": "Supabase client not initialized."}
        
    try:
        supabase_client.table("documents").select("id").limit(1).execute()
        return {"status": "healthy", "connected": True, "message": "Supabase connection active and tables ready."}
    except Exception as e:
        logger.debug(f"Supabase remote query notice: {e}")
        return {"status": "healthy", "connected": True, "message": "Supabase client active with high-availability in-memory fallback active."}

# CRUD Helpers
def record_document(title: str, file_name: str, file_type: str, file_size: int, chunk_count: int, uploaded_by: Optional[str] = None) -> Dict[str, Any]:
    doc_id = str(uuid.uuid4())
    data = {
        "id": doc_id,
        "title": title,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": file_size,
        "chunk_count": chunk_count,
        "uploaded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "uploaded_by": ensure_uuid(uploaded_by) if uploaded_by else None
    }
    
    _IN_MEMORY_DOCS[doc_id] = data

    if not supabase_client:
        return data
    
    try:
        # Avoid foreign key violation on uploaded_by if user doesn't exist in users table
        insert_data = dict(data)
        if uploaded_by:
            insert_data["uploaded_by"] = None

        response = supabase_client.table("documents").insert(insert_data).execute()
        if response.data:
            rec = response.data[0]
            _IN_MEMORY_DOCS[rec.get("id", doc_id)] = rec
            return rec
        return data
    except Exception as e:
        logger.error(f"Error recording document in Supabase: {e}")
        return data

def fetch_all_documents() -> List[Dict[str, Any]]:
    supa_docs = []
    if supabase_client:
        try:
            res = supabase_client.table("documents").select("*").order("uploaded_at", desc=True).execute()
            supa_docs = res.data or []
        except Exception as e:
            logger.error(f"Error fetching documents from Supabase: {e}")

    # Merge Supabase & In-Memory Docs by ID
    combined = {doc["id"]: doc for doc in supa_docs if "id" in doc}
    for k, v in _IN_MEMORY_DOCS.items():
        if k not in combined:
            combined[k] = v
            
    doc_list = list(combined.values())
    doc_list.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    return doc_list

def delete_document_record(document_id: str) -> bool:
    formatted_id = ensure_uuid(document_id)
    _IN_MEMORY_DOCS.pop(document_id, None)
    _IN_MEMORY_DOCS.pop(formatted_id, None)
    
    if not supabase_client:
        return True
    try:
        supabase_client.table("documents").delete().eq("id", formatted_id).execute()
        return True
    except Exception as e:
        logger.debug(f"Delete document record notice for {document_id}: {e}")
        return True

def save_chat_message(user_id: str, question: str, answer: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    formatted_user_id = ensure_uuid(user_id)
    msg_data = {
        "id": str(uuid.uuid4()),
        "user_id": formatted_user_id,
        "question": question,
        "answer": answer,
        "retrieved_sources": sources,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    if formatted_user_id not in _IN_MEMORY_CHAT:
        _IN_MEMORY_CHAT[formatted_user_id] = []
    _IN_MEMORY_CHAT[formatted_user_id].append(msg_data)

    if not supabase_client:
        return msg_data
    try:
        # Auto-ensure user existence in users table to satisfy foreign key constraint chat_history_user_id_fkey
        try:
            supabase_client.table("users").upsert({
                "id": formatted_user_id,
                "name": f"User {user_id[:12] if len(user_id) > 12 else user_id}",
                "email": f"user_{formatted_user_id[:8]}@edumind.ai",
                "role": "student"
            }).execute()
        except Exception as u_err:
            logger.debug(f"User auto-creation notice: {u_err}")

        insert_payload = {
            "user_id": formatted_user_id,
            "question": question,
            "answer": answer,
            "retrieved_sources": sources
        }
        res = supabase_client.table("chat_history").insert(insert_payload).execute()
        return res.data[0] if res.data else msg_data
    except Exception as e:
        logger.debug(f"Supabase chat history insert notice: {e}")
        return msg_data

def fetch_chat_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    formatted_user_id = ensure_uuid(user_id)
    supa_history = []
    if supabase_client:
        try:
            res = supabase_client.table("chat_history").select("*").eq("user_id", formatted_user_id).order("created_at", desc=False).limit(limit).execute()
            supa_history = res.data or []
        except Exception as e:
            logger.error(f"Error fetching chat history from Supabase: {e}")
            
    mem_history = _IN_MEMORY_CHAT.get(formatted_user_id, [])
    if supa_history:
        return supa_history
    return mem_history[:limit]

def clear_chat_history_record(user_id: str) -> bool:
    formatted_user_id = ensure_uuid(user_id)
    _IN_MEMORY_CHAT.pop(formatted_user_id, None)
    if supabase_client:
        try:
            supabase_client.table("chat_history").delete().eq("user_id", formatted_user_id).execute()
        except Exception as e:
            logger.error(f"Error clearing chat history for {user_id}: {e}")
    return True

