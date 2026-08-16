import re

import chromadb
from sentence_transformers import SentenceTransformer

from github_loader import clone_repository
from repo_reader import read_repository


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "gitdocs"


# ==========================================
# Embedding Model
# ==========================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================================
# ChromaDB
# ==========================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


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

                chunks.append(
                    chunk
                )

                metadatas.append({
                    "file": file_path
                })

            start += (
                chunk_size - overlap
            )


    # --------------------------------------
    # Check chunks
    # --------------------------------------

    if not chunks:

        raise ValueError(
            "No readable content found "
            "in the repository."
        )


    # --------------------------------------
    # Generate embeddings
    # --------------------------------------

    embeddings = embedding_model.encode(
        chunks,
        show_progress_bar=True
    ).tolist()


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