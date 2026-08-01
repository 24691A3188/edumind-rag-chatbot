import re
import logging
from typing import List

logger = logging.getLogger("edumind.text_splitter")

class SlidingWindowChunker:
    """
    Sliding Window Text Chunker configured for PRD specs:
    - Chunk Size: 500 words
    - Chunk Overlap: 100 words
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        """
        Normalizes whitespace and cleans unprintable characters.
        """
        if not text:
            return ""
        # Remove non-printable control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        # Collapse multiple whitespace/newlines into single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def split_text(self, text: str) -> List[str]:
        """
        Splits clean text into overlapping word chunks.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        words = cleaned.split(" ")
        total_words = len(words)

        if total_words <= self.chunk_size:
            return [" ".join(words)]

        chunks = []
        step = self.chunk_size - self.chunk_overlap

        for i in range(0, total_words, step):
            chunk_words = words[i : i + self.chunk_size]
            chunk_str = " ".join(chunk_words)
            
            # Avoid tiny trailing fragments under 15 words if previous chunk covers content
            if len(chunk_words) >= 15 or not chunks:
                chunks.append(chunk_str)

            if i + self.chunk_size >= total_words:
                break

        logger.info(f"Split {total_words} words into {len(chunks)} chunks (size={self.chunk_size}, overlap={self.chunk_overlap}).")
        return chunks

# Default Singleton Instance
chunker = SlidingWindowChunker(chunk_size=500, chunk_overlap=100)
