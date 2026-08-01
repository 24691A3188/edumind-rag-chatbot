import io
import logging
from typing import Union, List
import pandas as pd

try:
    from PyPDF2 import PdfReader
except ImportError:
    from pypdf import PdfReader

from docx import Document as DocxDocument

logger = logging.getLogger("edumind.upload")

class DocumentExtractor:
    """
    Multi-format document text extraction service.
    Supported formats: PDF, DOCX, TXT, FAQ CSV
    """
    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        pdf = PdfReader(io.BytesIO(file_bytes))
        extracted_text = []
        for idx, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                extracted_text.append(f"--- Page {idx + 1} ---\n" + text.strip())
        
        full_text = "\n\n".join(extracted_text)
        if not full_text.strip():
            raise ValueError("PDF document contains no readable text or image-only pages.")
        return full_text

    @staticmethod
    def extract_from_docx(file_bytes: bytes) -> str:
        doc = DocxDocument(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        full_text = "\n\n".join(paragraphs)
        if not full_text.strip():
            raise ValueError("DOCX document contains no readable text.")
        return full_text

    @staticmethod
    def extract_from_txt(file_bytes: bytes) -> str:
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1", errors="ignore")
            
        if not text.strip():
            raise ValueError("TXT document is empty.")
        return text.strip()

    @staticmethod
    def extract_from_csv_faq(file_bytes: bytes) -> str:
        """
        Parses CSV files containing Q&A data.
        Expects 'question' and 'answer' columns (case-insensitive).
        """
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Invalid CSV file format: {str(e)}")

        # Normalize column names to lowercase
        df.columns = [col.strip().lower() for col in df.columns]
        
        if "question" not in df.columns or "answer" not in df.columns:
            raise ValueError("FAQ CSV file must contain 'question' and 'answer' columns.")

        faq_entries = []
        for idx, row in df.iterrows():
            q = str(row["question"]).strip()
            a = str(row["answer"]).strip()
            if q and a and q.lower() != "nan" and a.lower() != "nan":
                faq_entries.append(f"FAQ Item #{idx + 1}\nQuestion: {q}\nAnswer: {a}")

        if not faq_entries:
            raise ValueError("FAQ CSV file contains no valid question-answer rows.")

        return "\n\n---\n\n".join(faq_entries)

    @classmethod
    def extract_text(cls, file_bytes: bytes, filename: str) -> str:
        if not filename or "." not in filename:
            raise ValueError("Invalid file name missing extension.")

        ext = filename.split(".")[-1].lower()
        logger.info(f"Extracting text from file '{filename}' (format=.{ext})...")

        if ext == "pdf":
            return cls.extract_from_pdf(file_bytes)
        elif ext == "docx":
            return cls.extract_from_docx(file_bytes)
        elif ext in ["txt", "md"]:
            return cls.extract_from_txt(file_bytes)
        elif ext == "csv":
            return cls.extract_from_csv_faq(file_bytes)
        else:
            raise ValueError(f"Unsupported file format '.{ext}'. Supported formats: PDF, DOCX, TXT, CSV.")

document_extractor = DocumentExtractor()
