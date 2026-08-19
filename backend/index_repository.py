import os
import re
import pickle

import chromadb

from sklearn.feature_extraction.text import TfidfVectorizer

from github_loader import clone_repository
from repo_reader import read_repository


# =========================================================
# CONFIGURATION
# =========================================================

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "gitdocs"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# =========================================================
# VALIDATE GITHUB URL
# =========================================================

def validate_github_url(github_url):

    if not github_url:

        raise ValueError(
            "GitHub repository URL is required."
        )

    pattern = r"^https://github\.com/[^/]+/[^/]+/?$"

    if not re.match(
        pattern,
        github_url.strip()
    ):

        raise ValueError(
            "Please enter a valid public GitHub repository URL."
        )


# =========================================================
# INDEX REPOSITORY
# =========================================================

def index_repository(github_url):

    github_url = github_url.strip()

    # =====================================================
    # VALIDATE URL
    # =====================================================

    validate_github_url(
        github_url
    )


    # =====================================================
    # CLONE REPOSITORY
    # =====================================================

    try:

        repo_path = clone_repository(
            github_url
        )

    except Exception as error:

        raise ValueError(
            f"Could not clone repository: {error}"
        )


    # =====================================================
    # READ REPOSITORY
    # =====================================================

    try:

        documents = read_repository(
            repo_path
        )

    except Exception as error:

        raise ValueError(
            f"Could not read repository files: {error}"
        )


    # =====================================================
    # CHECK DOCUMENTS
    # =====================================================

    if not documents:

        raise ValueError(
            "No supported files found in repository."
        )


    print(
        f"Found {len(documents)} useful files."
    )


    # =====================================================
    # CREATE CHUNKS
    # =====================================================

    chunks = []

    metadatas = []


    for document in documents:

        file_path = document["path"]

        content = document["content"]


        chunk_size = 2000

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


    # =====================================================
    # CHECK CHUNKS
    # =====================================================

    if not chunks:

        raise ValueError(
            "No readable content found."
        )


    # =====================================================
    # LIMIT CHUNKS
    # =====================================================

    MAX_CHUNKS = 300


    if len(chunks) > MAX_CHUNKS:

        print(
            f"Repository generated "
            f"{len(chunks)} chunks."
        )

        print(
            f"Limiting to "
            f"{MAX_CHUNKS} chunks."
        )

        chunks = chunks[
            :MAX_CHUNKS
        ]

        metadatas = metadatas[
            :MAX_CHUNKS
        ]


    print(
        f"Creating TF-IDF vectors for "
        f"{len(chunks)} chunks..."
    )


    # =====================================================
    # CREATE TF-IDF VECTORIZER
    # =====================================================

    vectorizer = TfidfVectorizer(

        max_features=768,

        stop_words="english"

    )


    try:

        matrix = vectorizer.fit_transform(
            chunks
        )

    except ValueError as error:

        raise ValueError(
            f"Could not create TF-IDF vectors: {error}"
        )


    embeddings = (
        matrix
        .toarray()
        .tolist()
    )


    print(
        f"TF-IDF vector dimension: "
        f"{len(embeddings[0])}"
    )


    # =====================================================
    # DELETE OLD CHROMA COLLECTION
    # =====================================================

    try:

        client.delete_collection(
            name=COLLECTION_NAME
        )

        print(
            "Old ChromaDB collection deleted."
        )

    except Exception:

        print(
            "No previous ChromaDB collection found."
        )


    # =====================================================
    # CREATE NEW COLLECTION
    # =====================================================

    collection = client.create_collection(

        name=COLLECTION_NAME

    )


    # =====================================================
    # CREATE IDS
    # =====================================================

    ids = [

        f"chunk-{i}"

        for i in range(
            len(chunks)
        )

    ]


    # =====================================================
    # STORE IN CHROMADB
    # =====================================================

    collection.add(

        ids=ids,

        documents=chunks,

        embeddings=embeddings,

        metadatas=metadatas

    )


    print(
        f"Stored {len(chunks)} chunks in ChromaDB."
    )


    # =====================================================
    # SAVE TF-IDF VECTORIZER
    # =====================================================

    os.makedirs(

        CHROMA_PATH,

        exist_ok=True

    )


    vectorizer_path = os.path.join(

        CHROMA_PATH,

        "vectorizer.pkl"

    )


    with open(

        vectorizer_path,

        "wb"

    ) as file:

        pickle.dump(

            vectorizer,

            file

        )


    print(
        f"Vectorizer saved to: "
        f"{vectorizer_path}"
    )


    # =====================================================
    # SUCCESS
    # =====================================================

    print(
        "Repository indexed successfully!"
    )


    return {

        "files": len(documents),

        "chunks": len(chunks)

    }