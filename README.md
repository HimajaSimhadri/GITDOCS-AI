# 🤖 GitDocs AI

**GitDocs AI** is an AI-powered developer assistant that allows users to connect a public GitHub repository and ask natural-language questions about its codebase.

Instead of manually searching through hundreds of files, developers can provide a GitHub repository URL and interact with the codebase through a simple conversational interface.

GitDocs AI uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant code and documentation from the repository and provide context-aware answers using **Google Gemini**.

---

## 🚀 Features

* 🔗 Connect a public GitHub repository
* 📥 Automatically clone GitHub repositories
* 📂 Read and filter supported source files
* ✂️ Split large files into smaller chunks
* 🧠 Generate semantic embeddings using Sentence Transformers
* 🗄️ Store embeddings in ChromaDB
* 🔎 Perform semantic similarity search
* 💬 Ask natural-language questions about the repository
* 📄 Identify relevant source files
* 🤖 Generate context-aware answers using Google Gemini
* 🌐 React-based web interface
* ⚡ FastAPI backend
* 🔐 Environment-based API key configuration
* ☁️ Deployable frontend and backend

---

# 🏗️ System Architecture

```text
                    GitHub Repository
                           │
                           ▼
                    GitHub Loader
                           │
                           ▼
                   Repository Reader
                           │
                           ▼
                    File Filtering
                           │
                           ▼
                     Text Chunking
                           │
                           ▼
                Sentence Transformer
                   Embedding Model
                           │
                           ▼
                       ChromaDB
                    Vector Database
                           │
                           │
                    User Question
                           │
                           ▼
                Question Embedding
                           │
                           ▼
                  Semantic Search
                           │
                           ▼
                Relevant Code Chunks
                           │
                           ▼
                   Context Builder
                           │
                           ▼
                    Google Gemini
                           │
                           ▼
                  Generated Answer
                           │
                           ▼
                    Source Files
```

---

# 🧠 How GitDocs AI Works

## 1. Repository Loading

The user provides a public GitHub repository URL.

GitDocs AI clones the repository and prepares it for processing.

```text
GitHub URL
     ↓
Clone Repository
```

---

## 2. Repository Reading

The repository is scanned recursively.

GitDocs AI extracts supported source-code and documentation files while ignoring unnecessary directories such as:

* `.git`
* `node_modules`
* `venv`
* `__pycache__`
* `dist`
* `build`

Supported file types include:

```text
.py
.js
.jsx
.ts
.tsx
.java
.html
.css
.json
.md
.sql
```

---

## 3. Text Chunking

Large source files are divided into smaller overlapping chunks.

The current implementation uses:

```text
Chunk size: 1000 characters
Overlap:    200 characters
```

This allows GitDocs AI to retrieve smaller, relevant sections of a repository instead of processing an entire file for every question.

---

## 4. Embedding Generation

Each text chunk is converted into a numerical vector using the Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

These embeddings capture the semantic meaning of the source-code and documentation.

---

## 5. Vector Storage

The generated embeddings are stored in **ChromaDB**.

Each stored chunk contains:

* Chunk ID
* Document content
* Embedding
* Source file metadata

Example:

```text
Chunk
 ├── ID
 ├── Code / Documentation
 ├── Embedding
 └── Source File
```

---

## 6. Question Retrieval

When the user asks a question, GitDocs AI generates an embedding for the question.

The question embedding is compared with the stored repository embeddings.

The most relevant chunks are retrieved from ChromaDB.

```text
User Question
      ↓
Question Embedding
      ↓
ChromaDB Similarity Search
      ↓
Top Relevant Chunks
```

---

## 7. Context Building

The retrieved chunks are combined into a context containing the relevant source files and code.

GitDocs AI also keeps track of the source files associated with the retrieved chunks.

---

## 8. AI Response Generation

The retrieved repository context is provided to **Google Gemini**.

Gemini generates a response based on the retrieved repository information.

This allows GitDocs AI to answer questions such as:

* What is the purpose of this project?
* What frontend technology is being used?
* Where is authentication implemented?
* Which file handles routing?
* How is the database configured?
* Which API creates a new user?
* How does the application process requests?
* What does this file do?

---

# 🛠️ Tech Stack

## Frontend

* React.js
* JavaScript
* CSS
* Vite
* Axios

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

## AI / RAG

* Retrieval-Augmented Generation (RAG)
* Sentence Transformers
* `all-MiniLM-L6-v2`
* Google Gemini

## Vector Database

* ChromaDB

## Repository Integration

* GitPython
* GitHub repositories

## Deployment

* Render

---

# 📁 Project Structure

```text
GITDOCS-AI/
│
├── backend/
│   ├── main.py
│   ├── github_loader.py
│   ├── repo_reader.py
│   ├── index_repository.py
│   ├── ingest_repo.py
│   ├── test_github.py
│   ├── test_reader.py
│   ├── requirements.txt
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── .gitignore
├── .env.example
└── README.md
```

