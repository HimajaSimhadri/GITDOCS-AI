import os
import re

import chromadb
from dotenv import load_dotenv
from google import genai

from backend.github_loader import clone_repository
from backend.repo_reader import read_repository


# ==========================================
# Load environment variables
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")


# ==========================================
# Gemini Client
# ==========================================

gemini_client = genai.Client(
    api_key=api_key
)


# ==========================================
# ChromaDB
# ==========================================

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "gitdocs"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# ==========================================
# Generate Gemini Embeddings
# ==========================================

def generate_embeddings(texts):

    embeddings = []

    for text in texts:

        response = gemini_client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )

        embeddings.append(
            response.embeddings[0].values
        )

    return embeddings


# ==========================================
# Validate GitHub URL
# ==========================================

def validate_github_url(github_url):

    if not github_url:
        raise ValueError(
            "GitHub repository URL is required."
        )

    pattern = r"^https://github\.com/[^/]+/[^/]+/?$"

    if not re.match(pattern, github_url.strip()):

        raise ValueError(
            "Please enter a valid public GitHub repository URL."
        )


# ==========================================
# Index Repository
# ==========================================

def index_repository(github_url):

    github_url = github_url.strip()

    # --------------------------------------
    # Validate URL
    # --------------------------------------

    validate_github_url(github_url)


    # --------------------------------------
    # Clone repository
    # --------------------------------------

    try:

        repo_path = clone_repository(
            github_url
        )

    except Exception as error:

        error_message = str(error).lower()

        if (
            "repository not found" in error_message
            or "not found" in error_message
            or "could not read from remote repository"
            in error_message
        ):

            raise ValueError(
                "Repository not found. "
                "Make sure the GitHub URL is correct "
                "and the repository is public."
            )

        raise ValueError(
            "Could not clone the repository. "
            "Make sure the repository is public "
            "and the URL is correct."
        )


    # --------------------------------------
    # Read repository files
    # --------------------------------------

    try:

        documents = read_repository(
            repo_path
        )

    except Exception as error:

        raise ValueError(
            f"Could not read repository files: {error}"
        )


    # --------------------------------------
    # Check files
    # --------------------------------------

    if not documents:

        raise ValueError(
            "No supported files found in repository."
        )


    # --------------------------------------
    # Get ChromaDB collection
    # --------------------------------------

    try:

        collection = client.get_collection(
            name=COLLECTION_NAME
        )

    except Exception:

        collection = client.create_collection(
            name=COLLECTION_NAME
        )


    # --------------------------------------
    # Clear old GitDocs data
    # --------------------------------------

    existing = collection.get()

    if existing["ids"]:

        collection.delete(
            ids=existing["ids"]
        )


    # --------------------------------------
    # Create chunks
    # --------------------------------------

    chunks = []
    metadatas = []

    for document in documents:

        file_path = document["path"]
        content = document["content"]

        chunk_size = 1000
        overlap = 200

        start = 0

        while start < len(content):

            end = start + chunk_size

            chunk = content[start:end]

            if chunk.strip():

                chunks.append(chunk)

                metadatas.append({
                    "file": file_path
                })

            start += chunk_size - overlap


    # --------------------------------------
    # Check chunks
    # --------------------------------------

    if not chunks:

        raise ValueError(
            "No readable content found "
            "in the repository."
        )


    # --------------------------------------
    # Generate Gemini embeddings
    # --------------------------------------

    print(
        f"Generating embeddings for {len(chunks)} chunks..."
    )

    embeddings = generate_embeddings(
        chunks
    )


    # --------------------------------------
    # Create IDs
    # --------------------------------------

    ids = [
        f"chunk-{i}"
        for i in range(len(chunks))
    ]


    # --------------------------------------
    # Store in ChromaDB
    # --------------------------------------

    collection.add(

        ids=ids,

        documents=chunks,

        embeddings=embeddings,

        metadatas=metadatas
    )


    # --------------------------------------
    # Return result
    # --------------------------------------

    return {

        "files": len(documents),

        "chunks": len(chunks)

    }
