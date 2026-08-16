import os

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from google import genai

from index_repository import index_repository


# ==========================================
# Load environment variables
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")


# ==========================================
# Gemini
# ==========================================

gemini_client = genai.Client(
    api_key=api_key
)


# ==========================================
# Embedding Model
# ==========================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================================
# ChromaDB
# ==========================================

chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = chroma_client.get_collection(
    name="gitdocs"
)


# ==========================================
# FastAPI
# ==========================================

app = FastAPI(
    title="GitDocs AI",
    description="RAG-powered GitHub Repository Assistant"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================
# Request Models
# ==========================================

class Question(BaseModel):
    question: str


class RepositoryRequest(BaseModel):
    url: str


# ==========================================
# Home
# ==========================================

@app.get("/")
def home():

    return {
        "message": "GitDocs AI backend is running!"
    }


# ==========================================
# Index GitHub Repository
# ==========================================

@app.post("/index")
def index_github_repository(
    data: RepositoryRequest
):

    try:

        result = index_repository(
            data.url
        )

        return {
            "message": "Repository indexed successfully!",
            "files": result["files"],
            "chunks": result["chunks"]
        }

    except Exception as error:

        return {
            "message": "Failed to index repository",
            "error": str(error)
        }


# ==========================================
# Ask Question
# ==========================================

@app.post("/ask")
def ask_question(
    data: Question
):

    question = data.question


    # ======================================
    # Create question embedding
    # ======================================

    question_embedding = embedding_model.encode(
        question
    ).tolist()


    # ======================================
    # Search ChromaDB
    # ======================================

    results = collection.query(

        query_embeddings=[
            question_embedding
        ],

        n_results=8
    )


    # ======================================
    # Get retrieved documents
    # ======================================

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]


    # ======================================
    # Build context with source files
    # ======================================

    context_parts = []

    sources = []

    for i, document in enumerate(documents):

        if i < len(metadatas):

            metadata = metadatas[i]

            file_name = metadata.get(
                "file",
                "Unknown file"
            )

        else:

            file_name = "Unknown file"


        # Add source to list
        if file_name != "Unknown file" and file_name not in sources:

            sources.append(file_name)


        # Add file + document to context
        context_parts.append(
            f"FILE: {file_name}\n\n{document}"
        )


    context = "\n\n".join(
        context_parts
    )


    # ======================================
    # RAG Prompt
    # ======================================

    prompt = f"""
You are GitDocs AI, an AI assistant for answering
questions about a software repository.

Use ONLY the repository context provided below.

IMPORTANT RULES:

1. Answer using the repository context.
2. If the answer is present in the context,
   you MUST answer it.
3. Do not say you couldn't find the information
   when the context contains the answer.
4. Do not invent information.
5. Keep the answer clear and concise.
6. If possible, mention the relevant source file.
7. If the context genuinely does not contain
   the answer, clearly say that the information
   was not found in the repository context.

REPOSITORY CONTEXT:

{context}


USER QUESTION:

{question}


ANSWER:
"""


    # ======================================
    # Gemini
    # ======================================

    response = gemini_client.models.generate_content(

        model="gemini-3.6-flash",

        contents=prompt
    )


    # ======================================
    # Response
    # ======================================

    return {

        "answer": response.text,

        "sources": sources

    }