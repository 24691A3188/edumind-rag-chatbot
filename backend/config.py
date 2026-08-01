import os
import logging
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("edumind.config")

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduMind AI RAG Chatbot"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8001"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

    # Supabase Credentials
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-supabase-project.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "your-supabase-anon-key")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-supabase-service-role-key")

    # Pinecone Credentials
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "your-pinecone-api-key")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "edumind-knowledge-base")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")

    # Embedding Model Settings
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-004")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))

    # Google Gemini Credentials
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    def is_supabase_configured(self) -> bool:
        return bool(
            self.SUPABASE_URL 
            and "your-supabase" not in self.SUPABASE_URL 
            and self.SUPABASE_ANON_KEY 
            and "your-supabase" not in self.SUPABASE_ANON_KEY
        )

    def is_pinecone_configured(self) -> bool:
        return bool(
            self.PINECONE_API_KEY 
            and "your-pinecone" not in self.PINECONE_API_KEY
        )

    def is_gemini_configured(self) -> bool:
        return bool(
            self.GEMINI_API_KEY 
            and "your-gemini" not in self.GEMINI_API_KEY
        )

settings = Settings()
