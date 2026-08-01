import logging
from typing import List, Dict, Any
from backend.config import settings

logger = logging.getLogger("edumind.embeddings")

class EmbeddingEngine:
    def __init__(self):
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self._is_loaded = False

    def _load_model(self):
        if self._is_loaded and self.model is not None:
            return
        
        try:
            logger.info(f"Loading SentenceTransformer model '{self.model_name}'...")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self._is_loaded = True
            
            # Verify dimension match
            test_vector = self.model.encode("test string", convert_to_numpy=True)
            actual_dim = len(test_vector)
            if actual_dim != self.dimension:
                logger.warning(f"Embedding dimension mismatch: Model produces {actual_dim} dims, expected {self.dimension}. Updating target dimension.")
                self.dimension = actual_dim

            logger.info(f"Embedding model '{self.model_name}' loaded successfully (dimension={self.dimension}).")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model '{self.model_name}': {e}")
            self._is_loaded = False

    def generate_embedding(self, text: str) -> List[float]:
        self._load_model()
        if not self._is_loaded or self.model is None:
            # Fallback mock 384-length vector if model loading fails
            logger.warning("Embedding model unavailable. Returning mock zero vector.")
            return [0.0] * self.dimension
            
        try:
            vec = self.model.encode(text, convert_to_numpy=True)
            return vec.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            return [0.0] * self.dimension

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        self._load_model()
        if not self._is_loaded or self.model is None:
            logger.warning("Embedding model unavailable. Returning mock zero vectors.")
            return [[0.0] * self.dimension for _ in texts]

        try:
            vecs = self.model.encode(texts, convert_to_numpy=True, batch_size=32)
            return [v.tolist() for v in vecs]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[0.0] * self.dimension for _ in texts]

    def check_status(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "configured_dimension": self.dimension,
            "is_loaded": self._is_loaded,
            "status": "ready" if self._is_loaded or self.model is not None else "lazy_unloaded"
        }

# Global Singleton Embedding Engine
embedding_engine = EmbeddingEngine()
