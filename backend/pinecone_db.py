import logging
from typing import Dict, Any, List, Optional
from pinecone import Pinecone, ServerlessSpec
from backend.config import settings

logger = logging.getLogger("edumind.pinecone")

class PineconeManager:
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.is_connected = False
        self._init_pinecone()

    def _init_pinecone(self):
        if not settings.is_pinecone_configured():
            logger.warning("Pinecone API key not configured or placeholder used. Pinecone operating in mock/unconfigured mode.")
            self.is_connected = False
            return

        try:
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            self.is_connected = True
            logger.info(f"Pinecone connected and index '{settings.PINECONE_INDEX_NAME}' is ready.")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.is_connected = False

    def _ensure_index_exists(self):
        if not self.pc:
            return
        
        try:
            existing_indices = [idx.name for idx in self.pc.list_indexes()]
            if settings.PINECONE_INDEX_NAME not in existing_indices:
                logger.info(f"Creating Pinecone index '{settings.PINECONE_INDEX_NAME}' (dim={settings.EMBEDDING_DIMENSION}, metric=cosine)...")
                self.pc.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=settings.EMBEDDING_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=settings.PINECONE_CLOUD,
                        region=settings.PINECONE_REGION
                    )
                )
                logger.info(f"Pinecone index '{settings.PINECONE_INDEX_NAME}' created successfully.")
        except Exception as e:
            logger.error(f"Error checking/creating Pinecone index: {e}")

    def check_status(self) -> Dict[str, Any]:
        if not settings.is_pinecone_configured():
            return {
                "status": "unconfigured",
                "connected": False,
                "index_name": settings.PINECONE_INDEX_NAME,
                "dimension": settings.EMBEDDING_DIMENSION,
                "message": "Pinecone API key missing or placeholder."
            }

        if not self.is_connected or not self.index:
            return {
                "status": "disconnected",
                "connected": False,
                "index_name": settings.PINECONE_INDEX_NAME,
                "dimension": settings.EMBEDDING_DIMENSION,
                "message": "Pinecone client initialized but index connection failed."
            }

        try:
            stats = self.index.describe_index_stats()
            return {
                "status": "healthy",
                "connected": True,
                "index_name": settings.PINECONE_INDEX_NAME,
                "dimension": settings.EMBEDDING_DIMENSION,
                "total_vector_count": stats.get("total_vector_count", 0),
                "message": "Pinecone vector index active and connected."
            }
        except Exception as e:
            return {
                "status": "degraded",
                "connected": True,
                "index_name": settings.PINECONE_INDEX_NAME,
                "dimension": settings.EMBEDDING_DIMENSION,
                "message": f"Connection active, stats query returned: {str(e)}"
            }

    def get_index_stats(self) -> Dict[str, Any]:
        status_info = self.check_status()
        total_vectors = 0
        namespaces = {}
        if self.is_connected and self.index:
            try:
                raw_stats = self.index.describe_index_stats()
                total_vectors = raw_stats.get("total_vector_count", 0)
                raw_namespaces = raw_stats.get("namespaces", {})
                if isinstance(raw_namespaces, dict):
                    for ns_k, ns_v in raw_namespaces.items():
                        v_count = getattr(ns_v, "vector_count", 0) if hasattr(ns_v, "vector_count") else (ns_v.get("vector_count", 0) if isinstance(ns_v, dict) else 0)
                        namespaces[str(ns_k)] = {"vector_count": v_count}
            except Exception as e:
                logger.error(f"Error fetching detailed Pinecone stats: {e}")

        return {
            "index_name": settings.PINECONE_INDEX_NAME,
            "dimension": settings.EMBEDDING_DIMENSION,
            "metric": "cosine",
            "cloud": settings.PINECONE_CLOUD,
            "region": settings.PINECONE_REGION,
            "total_vector_count": total_vectors,
            "namespaces": namespaces,
            "connected": self.is_connected,
            "status": status_info.get("status", "unknown")
        }

    def upsert_vectors(self, vectors: List[tuple]) -> bool:
        if not self.is_connected or not self.index:
            logger.warning("Pinecone not connected. Vector upsert skipped.")
            return False
        try:
            self.index.upsert(vectors=vectors)
            return True
        except Exception as e:
            logger.warning(f"Upsert failed, checking if index exists: {e}")
            self._ensure_index_exists()
            try:
                self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
                self.index.upsert(vectors=vectors)
                return True
            except Exception as retry_err:
                logger.error(f"Failed to upsert vectors to Pinecone: {retry_err}")
                return False

    def query_similarity(self, vector: List[float], top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.is_connected or not self.index:
            logger.warning("Pinecone not connected. Vector query returned empty results.")
            return {"matches": []}
        try:
            return self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
        except Exception as e:
            logger.error(f"Failed to query Pinecone vector index: {e}")
            return {"matches": []}

    def delete_by_document(self, document_id: str) -> bool:
        if not self.is_connected or not self.index:
            return True
        try:
            self.index.delete(filter={"document_id": {"$eq": str(document_id)}})
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors for document {document_id}: {e}")
            return False

# Global Pinecone Manager Singleton
pinecone_manager = PineconeManager()
