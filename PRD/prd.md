# Product Requirements Document (PRD)

# AI-Powered Contextual Website Chatbot with Memory

## Version
1.0

## Author
Harshitha

## Project Type
Intermediate AI / Machine Learning Project

---

# 1. Project Overview

## Project Title

**AI-Powered Contextual Website Chatbot with Memory**

## Description

Develop an intelligent website chatbot that leverages **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware, and personalized responses from uploaded documents, FAQs, and internal knowledge.

Unlike traditional chatbots, this chatbot retrieves relevant information from a vector database before generating answers, reducing hallucinations and improving response accuracy.

The chatbot maintains conversational memory, enabling follow-up questions while preserving context.

This project follows the RAG architecture introduced in the provided Day-1 and Day-2 learning materials.

---

# 2. Problem Statement

Large Language Models have three major limitations:

- No knowledge of private company data
- Outdated information
- Hallucinated responses

Organizations require an AI assistant capable of answering questions using their own documents rather than relying solely on pre-trained knowledge.

---

# 3. Objectives

The chatbot should:

- Answer questions from uploaded documents
- Search knowledge using semantic similarity
- Remember previous conversations
- Allow administrators to upload new documents
- Generate grounded responses using retrieved context
- Reduce hallucinations through Retrieval-Augmented Generation

---

# 4. Target Users

### Students

Ask questions about courses, assignments, and college policies.

### Customers

Get product information, pricing, shipping details, and FAQs.

### Employees

Access HR policies and internal documents.

### Administrators

Manage chatbot knowledge by uploading documents.

---

# 5. Core Features

## 5.1 Website Chat Interface

### Description

A modern ChatGPT-like interface integrated into a website.

### Features

- Real-time messaging
- Typing animation
- Suggested prompts
- Chat history
- Responsive UI

---

## 5.2 Document Upload

Supported formats:

- PDF
- DOCX
- TXT
- FAQ CSV

Uploaded documents are automatically processed and stored.

---

## 5.3 Document Processing Pipeline

```
Document Upload

↓

Extract Text

↓

Clean Text

↓

Chunking

↓

Embedding Generation

↓

Store in Pinecone
```

### Chunk Size

500 words

### Chunk Overlap

100 words

---

## 5.4 Semantic Search

When the user asks a question:

```
User Question

↓

Embedding

↓

Pinecone Search

↓

Top 5 Relevant Chunks

↓

Context
```

---

## 5.5 Context-Aware Response Generation

The chatbot generates answers using:

- Retrieved document context
- Previous conversation history
- User question

Prompt Template

```
You are an intelligent educational assistant.

Use ONLY the provided context.

Conversation History:

{memory}

Retrieved Context:

{chunks}

Question:

{query}

Generate an accurate answer.
```

---

## 5.6 Conversation Memory

The chatbot stores conversation history.

Example

User:

> Tell me about the AI course.

Later:

> How much does it cost?

The chatbot understands "it" refers to the AI course.

---

## 5.7 Admin Dashboard

Admin can

- Login
- Upload documents
- Upload FAQs
- View uploaded files
- Delete documents
- Monitor chatbot knowledge

---

# 6. Functional Requirements

## User Module

- Open website
- Start conversation
- Ask questions
- Receive AI responses
- View chat history
- Continue conversations

---

## Admin Module

- Login securely
- Upload documents
- Upload FAQ files
- Delete outdated files
- Refresh vector database

---

## AI Module

- Extract text
- Chunk documents
- Generate embeddings
- Store vectors
- Perform semantic search
- Build prompts
- Generate answers
- Save chat history

---

# 7. Non-Functional Requirements

- Fast response (<3 seconds)
- Mobile responsive
- Secure API
- Easy document updates
- Scalable architecture
- Maintainable codebase

---

# 8. Technology Stack

## Frontend

- Streamlit
- HTML
- CSS

---

## Backend

- FastAPI

---

## Database

Supabase

---

## Vector Database

Pinecone

---

## Embedding Model

```
sentence-transformers/all-MiniLM-L6-v2
```

(Hugging Face)

---

## LLM

OpenAI GPT API

---

# 9. System Architecture

```
                    Admin

                      │

                Upload Document

                      │

               Text Extraction

                      │

                  Chunking

                      │

                 Embeddings

                      │

                   Pinecone

------------------------------------------------

                    User

                      │

                Website Chat

                      │

                 Ask Question

                      │

             Generate Embedding

                      │

             Semantic Retrieval

                      │

            Top Relevant Chunks

                      │

         Conversation Memory

                      │

                OpenAI GPT

                      │

             Generated Answer

                      │

          Store History (Supabase)
```

---

# 10. Project Workflow

```
User

↓

Ask Question

↓

Backend API

↓

Generate Embedding

↓

Search Pinecone

↓

Retrieve Chunks

↓

Load Conversation Memory

↓

Create Prompt

↓

OpenAI GPT

↓

Generate Answer

↓

Store Chat History

↓

Return Response
```

---

# 11. Folder Structure

```
rag-chatbot/

│

├── backend/

│   ├── app.py

│   ├── rag.py

│   ├── embeddings.py

│   ├── pinecone_db.py

│   ├── upload.py

│   ├── memory.py

│   ├── database.py

│

├── frontend/

│   └── streamlit_app.py

│

├── documents/

├── vectorstore/

├── utils/

├── requirements.txt

├── .env

└── README.md
```

---

# 12. Database Design

## Users

| Field | Type |
|------|------|
| id | UUID |
| name | Text |
| email | Text |

---

## Chat History

| Field | Type |
|------|------|
| id | UUID |
| user_id | UUID |
| question | Text |
| answer | Text |
| created_at | Timestamp |

---

## Documents

| Field | Type |
|------|------|
| id | UUID |
| title | Text |
| file_name | Text |
| uploaded_at | Timestamp |

---

## FAQ

| Field | Type |
|------|------|
| id | UUID |
| question | Text |
| answer | Text |

---

# 13. API Endpoints

## Upload Document

```
POST /upload
```

---

## Chat

```
POST /chat
```

---

## Get Chat History

```
GET /history
```

---

## Delete Chat History

```
DELETE /history
```

---

## Get Documents

```
GET /documents
```

---

## Delete Document

```
DELETE /document
```

---

# 14. User Flow

```
Open Website

↓

Open Chatbot

↓

Ask Question

↓

Backend

↓

Embedding

↓

Pinecone

↓

Retrieve Context

↓

Conversation Memory

↓

OpenAI

↓

Answer

↓

Store History
```

---

# 15. Admin Flow

```
Login

↓

Upload PDF

↓

Extract Text

↓

Chunk Document

↓

Generate Embeddings

↓

Store in Pinecone

↓

Knowledge Updated
```

---

# 16. UI Pages

## Home

- Hero Section
- About Project
- Features
- Start Chat Button

---

## Chat Page

- Chat Window
- Message History
- Suggested Questions
- Typing Animation

---

## Admin Login

- Email
- Password

---

## Admin Dashboard

- Upload PDF
- Upload DOCX
- Upload TXT
- Upload FAQ CSV
- View Documents
- Delete Documents

---

## About

- Project Overview
- Technologies Used
- RAG Architecture

---

# 17. Future Enhancements

- Voice chatbot
- Image-based document search
- Multi-language support
- User authentication
- Analytics dashboard
- Feedback learning
- Citation highlighting
- Document versioning

---

# 18. Success Criteria

The project will be considered successful if it can:

- Upload documents successfully
- Create vector embeddings
- Retrieve relevant document chunks
- Generate context-aware answers
- Maintain conversation history
- Reduce hallucinations
- Provide fast responses
- Allow admin knowledge management

---

# 19. Expected Outcome

An intelligent AI-powered chatbot capable of answering questions using uploaded documents through Retrieval-Augmented Generation (RAG), semantic search, and conversational memory, providing accurate and grounded responses suitable for educational institutions, businesses, and customer support websites.