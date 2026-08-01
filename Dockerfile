# Production Dockerfile for EduMind AI FastAPI Backend Server
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SentenceTransformer embedding model into container layer for instant startup
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application source code
COPY . .

# Expose backend port
EXPOSE 8000

# Launch Uvicorn server using shell form to expand $PORT dynamically on Render / Railway
CMD sh -c "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"
