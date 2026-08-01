import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types
from backend.config import settings

logger = logging.getLogger("edumind.embeddings")

class EmbeddingEngine:
    """
    Lightweight Cloud Embedding Engine powered by Google Gemini API.
    Replaces local PyTorch / SentenceTransformer models to eliminate memory overhead
    and prevent Render Free tier 502/OOM errors.
    """
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME or "text-embedding-004"
        self.dimension = settings.EMBEDDING_DIMENSION or 384

    def _get_client(self) -> genai.Client:
        key = settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY
        return genai.Client(api_key=key)

    def _embed_content_with_fallback(self, contents: Any) -> List[Any]:
        client = self._get_client()
        models_to_try = [self.model_name, "text-embedding-004", "gemini-embedding-001"]
        # De-duplicate model candidates while preserving preference order
        seen = set()
        unique_models = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

        last_error = None
        for model_candidate in unique_models:
            try:
                config = types.EmbedContentConfig(output_dimensionality=self.dimension)
                res = client.models.embed_content(
                    model=model_candidate,
                    contents=contents,
                    config=config
                )
                if res and res.embeddings:
                    return res.embeddings
            except Exception as e:
                last_error = e
                logger.warning(f"Embedding attempt with model '{model_candidate}' failed: {e}. Trying fallback...")
                continue
                
        if last_error:
            raise last_error
        raise RuntimeError("No suitable Gemini embedding model available.")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a 384-dimensional dense vector embedding for a single string query.
        """
        if not text or not text.strip():
            return [0.0] * self.dimension

        if not settings.is_gemini_configured():
            logger.warning("Gemini API key not configured. Returning fallback zero vector.")
            return [0.0] * self.dimension

        try:
            embeddings = self._embed_content_with_fallback(contents=text.strip())
            if embeddings and len(embeddings) > 0 and hasattr(embeddings[0], 'values'):
                vec = list(embeddings[0].values)
                if len(vec) == self.dimension:
                    return vec
                elif len(vec) > self.dimension:
                    return vec[:self.dimension]
                else:
                    return vec + [0.0] * (self.dimension - len(vec))
            return [0.0] * self.dimension
        except Exception as e:
            logger.error(f"Error generating Gemini embedding: {e}")
            return [0.0] * self.dimension

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates 384-dimensional dense vector embeddings for a list of text chunks.
        Processes in batches of 32 to respect API batch boundaries.
        """
        if not texts:
            return []

        if not settings.is_gemini_configured():
            logger.warning("Gemini API key not configured. Returning fallback zero vectors.")
            return [[0.0] * self.dimension for _ in texts]

        results: List[List[float]] = []
        batch_size = 32

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            clean_batch = [t.strip() if t and t.strip() else " " for t in batch]
            try:
                embeddings = self._embed_content_with_fallback(contents=clean_batch)
                for emb in embeddings:
                    if hasattr(emb, 'values') and emb.values:
                        vec = list(emb.values)
                        if len(vec) == self.dimension:
                            results.append(vec)
                        elif len(vec) > self.dimension:
                            results.append(vec[:self.dimension])
                        else:
                            results.append(vec + [0.0] * (self.dimension - len(vec)))
                    else:
                        results.append([0.0] * self.dimension)
            except Exception as e:
                logger.error(f"Error generating batch Gemini embeddings for batch index {i}: {e}")
                # Fallback per-text attempt if batch fails
                for single_text in clean_batch:
                    results.append(self.generate_embedding(single_text))

        return results

    def check_status(self) -> Dict[str, Any]:
        """
        Returns status and configuration details of the Cloud Gemini Embedding Engine.
        """
        is_ready = settings.is_gemini_configured()
        return {
            "model_name": self.model_name,
            "configured_dimension": self.dimension,
            "provider": "Google Gemini API",
            "ready": is_ready,
            "status": "ready" if is_ready else "unconfigured"
        }

# Alias class name as requested
GeminiEmbeddingEngine = EmbeddingEngine

# Global Singleton Embedding Engine
embedding_engine = GeminiEmbeddingEngine()
