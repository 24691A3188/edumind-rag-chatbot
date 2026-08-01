import logging
from typing import List, Dict, Any
from backend.database import fetch_chat_history

logger = logging.getLogger("edumind.memory")

class ConversationMemoryManager:
    """
    Session-based Conversational Memory Manager.
    Retrieves previous user questions and AI answers from Supabase chat_history table
    and formats them for injection into RAG prompts.
    """
    @staticmethod
    def get_formatted_memory(user_id: str, limit: int = 5) -> str:
        """
        Retrieves past conversation turns for a user and formats them into a clean chat log string.
        """
        if not user_id or not user_id.strip():
            return "No previous conversation history."

        try:
            records = fetch_chat_history(user_id=user_id, limit=limit)
            if not records:
                return "No previous conversation history."

            formatted_turns = []
            for item in records:
                q = item.get("question", "").strip()
                a = item.get("answer", "").strip()
                if q and a:
                    formatted_turns.append(f"User: {q}")
                    formatted_turns.append(f"Assistant: {a}")

            if not formatted_turns:
                return "No previous conversation history."

            logger.info(f"Retrieved {len(records)} chat history items for user '{user_id}'.")
            return "\n".join(formatted_turns)
        except Exception as e:
            logger.error(f"Error fetching conversation memory for user '{user_id}': {e}")
            return "No previous conversation history."

memory_manager = ConversationMemoryManager()
