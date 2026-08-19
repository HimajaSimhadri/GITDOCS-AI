import os
import pickle

import chromadb

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

from index_repository import index_repository


# ==========================================
# Environment
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found"
    )


# ==========================================
# Gemini
# ==========================================

gemini_client = genai.Client(
    api_key=api_key
)


# ==========================================
# Chroma
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
    allow_headers=["*"]
)


# ==========================================
# Models
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
        "message":
        "GitDocs AI backend is running!"
    }


# ==========================================
# Index
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
            "message":
            "Repository indexed successfully!",
            "files":
            result["files"],
            "chunks":
            result["chunks"]
        }

    except Exception as error:

        print(
            "INDEX ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# Ask
# ==========================================

@app.post("/ask")
def ask_question(
    data: Question
):

    question = data.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        # Load vectorizer
        vectorizer_path = os.path.join(
            "chroma_db",
            "vectorizer.pkl"
        )

        if not os.path.exists(
            vectorizer_path
        ):

            raise ValueError(
                "Please index a repository first."
            )

        with open(
            vectorizer_path,
            "rb"
        ) as file:

            vectorizer = pickle.load(file)

        # Convert question
        question_vector = (
            vectorizer
            .transform([question])
            .toarray()
            .tolist()[0]
        )

        # Search
        results = collection.query(

            query_embeddings=[
                question_vector
            ],

            n_results=5
        )

        documents = results["documents"][0]

        metadatas = results["metadatas"][0]

        # Build context
        context_parts = []

        sources = []

        for i, document in enumerate(
            documents
        ):

            file_name = metadatas[i].get(
                "file",
                "Unknown"
            )

            if file_name not in sources:

                sources.append(
                    file_name
                )

            context_parts.append(
                f"FILE: {file_name}\n\n{document}"
            )

        context = "\n\n".join(
            context_parts
        )

        # Prompt
        prompt = f"""
You are GitDocs AI.

You answer questions about a software repository.

Use ONLY the repository context below.

Do not invent information.

If the answer is not present in the context,
say that it was not found.

Mention relevant source files when possible.

REPOSITORY CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

        # Gemini ONLY for answer generation
        response = gemini_client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt
        )

        return {
            "answer": response.text,
            "sources": sources
        }

    except Exception as error:

        print(
            "ASK ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )