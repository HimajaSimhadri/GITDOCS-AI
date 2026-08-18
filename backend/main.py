import os

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
# ChromaDB
# ==========================================

chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)
try:
    collection = chroma_client.get_collection(
        name="gitdocs"
    )
except Exception:
    collection = chroma_client.create_collection(
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

    
    allow_origins=["*"],
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
# Gemini Embedding
# ==========================================

def generate_query_embedding(text):

    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values


# ==========================================
# Home
# ==========================================

@app.get("/")
def home():

    return {
        "message": "GitDocs AI backend is running!"
    }


# ==========================================
# Index Repository
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

    question_embedding = generate_query_embedding(
        question
    )


    # ======================================
    # Search ChromaDB
    # ======================================

    results = collection.query(

        query_embeddings=[
            question_embedding
        ],

        n_results=3
    )


    # ======================================
    # Get retrieved documents
    # ======================================

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]


    # ======================================
    # Build context
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


        if (
            file_name != "Unknown file"
            and file_name not in sources
        ):

            sources.append(file_name)


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
3. Do not invent information.
4. Keep the answer clear and concise.
5. Mention relevant source files when possible.
6. If the context does not contain the answer,
   clearly say that it was not found.

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
