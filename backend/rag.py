import os
import logging
from typing import Dict, Any, List
from google import genai
from backend.config import settings
from backend.embeddings import embedding_engine
from backend.pinecone_db import pinecone_manager
from backend.memory import memory_manager
from backend.database import save_chat_message

logger = logging.getLogger("edumind.rag")

PROMPT_TEMPLATE = """You are an intelligent educational assistant (EduMind AI).

Use ONLY the provided retrieved context and conversation history to answer the user's question. 
If the answer cannot be determined strictly from the provided context, state clearly: "I cannot find relevant information in the uploaded documents to answer your question." Do not make up facts or hallucinate.

Conversation History:
{memory}

Retrieved Context Chunks:
{chunks}

Question:
{query}

Generate a clear, accurate, and context-grounded answer:"""

class RAGEngine:
    """
    RAG Engine executing vector retrieval, memory assembly, prompt injection,
    and Google Gemini LLM answer synthesis.
    """
    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def generate_response(self, user_id: str, query: str) -> Dict[str, Any]:
        logger.info(f"Processing RAG query for user '{user_id}': '{query}'")

        # 1. Generate Query Vector Embedding (384-dim)
        query_embedding = embedding_engine.generate_embedding(query)

        # 2. Query Pinecone Vector Index
        search_results = pinecone_manager.query_similarity(vector=query_embedding, top_k=self.top_k)
        matches = search_results.get("matches", [])

        retrieved_chunks = []
        sources = []

        for match in matches:
            metadata = match.get("metadata", {})
            text_chunk = metadata.get("text", "")
            file_name = metadata.get("file_name", "Indexed Document")
            score = match.get("score", 0.0)

            if text_chunk:
                retrieved_chunks.append(text_chunk)
                snippet = text_chunk[:160] + "..." if len(text_chunk) > 160 else text_chunk
                sources.append({
                    "file_name": file_name,
                    "score": round(float(score), 4),
                    "chunk": snippet
                })

        context_str = "\n\n---\n\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."

        # 3. Load Conversational Memory
        memory_str = memory_manager.get_formatted_memory(user_id=user_id, limit=5)

        # 4. Assemble Prompt
        full_prompt = PROMPT_TEMPLATE.format(
            memory=memory_str,
            chunks=context_str,
            query=query
        )

        # 5. Invoke Google Gemini LLM API (or fallback if unconfigured)
        answer = self._invoke_llm(full_prompt, query, retrieved_chunks)

        # 6. Save Message & Sources to Supabase
        save_chat_message(
            user_id=user_id,
            question=query,
            answer=answer,
            sources=sources
        )

        return {
            "answer": answer,
            "sources": sources,
            "chunks_retrieved": len(retrieved_chunks)
        }

    def _invoke_llm(self, full_prompt: str, query: str, retrieved_chunks: List[str]) -> str:
        if not settings.is_gemini_configured():
            logger.warning("Gemini API key not configured or using placeholder. Returning context-grounded fallback response.")
            if not retrieved_chunks:
                return "I cannot find relevant information in the uploaded documents to answer your question."
            else:
                formatted_snippets = "\n\n".join([f"• Chunk {i+1}:\n{chunk.strip()}" for i, chunk in enumerate(retrieved_chunks[:3])])
                return f"Based on your uploaded documents ({len(retrieved_chunks)} relevant chunk(s) retrieved):\n\n{formatted_snippets}"

        try:
            api_key = settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY
            client = genai.Client(api_key=api_key)
            model_name = settings.GEMINI_MODEL or "gemini-flash-latest"
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            return "I cannot find relevant information in the uploaded documents to answer your question."
        except Exception as e:
            logger.error(f"Google Gemini API invocation error: {e}")
            if retrieved_chunks:
                formatted_snippets = "\n\n".join([f"• Context snippet {i+1}:\n{chunk.strip()[:400]}" for i, chunk in enumerate(retrieved_chunks[:3])])
                return f"Based on the retrieved document context:\n\n{formatted_snippets}"
            return "I cannot find relevant information in the uploaded documents to answer your question."

rag_engine = RAGEngine(top_k=5)
