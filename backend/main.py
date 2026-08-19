import os
import pickle
import time

import chromadb

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

from index_repository import index_repository


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")


# ============================================================
# GEMINI
# ============================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# CHROMADB
# ============================================================

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "gitdocs"

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


def get_collection():
    """
    ALWAYS get the latest ChromaDB collection.

    Important:
    index_repository() can delete and recreate the collection.
    Therefore we must NOT keep a global collection object.
    """

    try:

        collection = chroma_client.get_collection(
            name=COLLECTION_NAME
        )

        print(
            f"ChromaDB collection loaded: {COLLECTION_NAME}"
        )

        return collection

    except Exception as error:

        print(
            "ChromaDB collection does not exist yet."
        )

        return None


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="GitDocs AI",
    description="AI assistant for GitHub repositories"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# REQUEST MODELS
# ============================================================

class Question(BaseModel):

    question: str


class RepositoryRequest(BaseModel):

    url: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "GitDocs AI backend is running!"
    }


# ============================================================
# INDEX REPOSITORY
# ============================================================

@app.post("/index")
def index_repository_endpoint(
    data: RepositoryRequest
):

    try:

        print()
        print("=" * 60)
        print("INDEXING REPOSITORY")
        print("URL:", data.url)
        print("=" * 60)

        result = index_repository(
            data.url
        )

        print(
            "Repository indexing completed."
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

        print()
        print("=" * 60)
        print("INDEX ERROR")
        print(error)
        print("=" * 60)

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question(
    data: Question
):

    question = data.question.strip()

    print()
    print("=" * 60)
    print("NEW QUESTION")
    print("Question:", question)
    print("=" * 60)


    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question:

        raise HTTPException(

            status_code=400,

            detail="Question cannot be empty."
        )


    try:

        # ====================================================
        # LOAD VECTORIZER
        # ====================================================

        vectorizer_path = os.path.join(

            CHROMA_PATH,

            "vectorizer.pkl"
        )


        if not os.path.exists(
            vectorizer_path
        ):

            raise ValueError(

                "No indexed repository found. "
                "Please index a repository first."
            )


        print(
            "Loading TF-IDF vectorizer..."
        )


        with open(

            vectorizer_path,

            "rb"

        ) as file:

            vectorizer = pickle.load(
                file
            )


        # ====================================================
        # CREATE QUESTION VECTOR
        # ====================================================

        print(
            "Creating question vector..."
        )


        question_vector = (

            vectorizer

            .transform(
                [question]
            )

            .toarray()

            .tolist()[0]
        )


        print(
            "Question vector created."
        )

        print(
            "Vector dimensions:",
            len(question_vector)
        )


        # ====================================================
        # IMPORTANT FIX
        # GET FRESH CHROMA COLLECTION
        # ====================================================

        print(
            "Loading latest ChromaDB collection..."
        )


        collection = get_collection()


        if collection is None:

            raise ValueError(

                "ChromaDB collection not found. "
                "Please index the repository again."
            )


        # ====================================================
        # CHECK COLLECTION
        # ====================================================

        try:

            collection_count = (
                collection.count()
            )

        except Exception as error:

            print(
                "Could not read ChromaDB collection:",
                error
            )

            raise ValueError(

                "ChromaDB collection is unavailable. "
                "Please index the repository again."
            )


        print(
            "Chroma collection:",
            COLLECTION_NAME
        )

        print(
            "Documents in Chroma:",
            collection_count
        )


        if collection_count == 0:

            raise ValueError(

                "ChromaDB collection is empty. "
                "Please index the repository again."
            )


        # ====================================================
        # SEARCH CHROMA
        # ====================================================

        print(
            "Searching ChromaDB..."
        )


        results = collection.query(

            query_embeddings=[

                question_vector

            ],

            n_results=min(
                5,
                collection_count
            ),

            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )


        documents = results.get(
            "documents",
            [[]]
        )[0]


        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]


        distances = results.get(
            "distances",
            [[]]
        )[0]


        print()
        print(
            "========== CHROMA RESULTS =========="
        )

        print(
            "Results returned:",
            len(documents)
        )


        # ====================================================
        # NO RESULTS
        # ====================================================

        if not documents:

            return {

                "answer":
                "I could not find relevant information "
                "in the indexed repository.",

                "sources": []
            }


        # ====================================================
        # BUILD CONTEXT
        # ====================================================

        context_parts = []

        sources = []


        for index, document in enumerate(
            documents
        ):

            if index < len(metadatas):

                metadata = (
                    metadatas[index]
                    or {}
                )

            else:

                metadata = {}


            file_name = metadata.get(

                "file",

                "Unknown file"
            )


            if index < len(distances):

                distance = distances[index]

            else:

                distance = None


            print()
            print(
                f"--- RESULT {index + 1} ---"
            )

            print(
                "FILE:",
                file_name
            )

            print(
                "DISTANCE:",
                distance
            )


            if file_name not in sources:

                sources.append(
                    file_name
                )


            context_parts.append(

                f"""
FILE: {file_name}

{document}
"""
            )


        context = "\n\n".join(
            context_parts
        )


        # ====================================================
        # GEMINI PROMPT
        # ====================================================

        prompt = f"""
You are GitDocs AI, an AI assistant that understands
GitHub repositories.

Answer the user's question using ONLY the repository
context provided below.

IMPORTANT RULES:

1. Do not invent information.
2. Do not use outside knowledge.
3. If the answer exists in the context, explain it clearly.
4. Mention the relevant source file names.
5. If the answer cannot be determined from the context,
   clearly say that it was not found.
6. Prefer a concise but useful answer.
7. When possible, explain how the relevant code works.

==================================================
REPOSITORY CONTEXT
==================================================

{context}

==================================================
USER QUESTION
==================================================

{question}

==================================================
ANSWER
==================================================
"""


        # ====================================================
        # GEMINI WITH RETRY
        # ====================================================

        response = None

        max_attempts = 2


        for attempt in range(
            1,
            max_attempts + 1
        ):

            try:

                print(
                    f"Gemini attempt "
                    f"{attempt}/{max_attempts}"
                )


                response = (

                    gemini_client
                    .models
                    .generate_content(

                        model="gemini-3.6-flash",

                        contents=prompt
                    )
                )


                print(
                    "Gemini response received."
                )

                break


            except Exception as error:

                error_message = str(
                    error
                )


                print(
                    "Gemini ERROR:"
                )

                print(
                    error_message
                )


                if attempt < max_attempts:

                    print(
                        "Gemini temporarily unavailable."
                    )

                    time.sleep(3)

                else:

                    raise


        # ====================================================
        # GEMINI RESPONSE
        # ====================================================

        if response is None:

            raise ValueError(
                "Gemini did not return a response."
            )


        answer = getattr(

            response,

            "text",

            None
        )


        if not answer:

            answer = (

                "Gemini returned an empty response."
            )


        print(
            "Answer generated successfully."
        )

        print(
            "Sources:",
            sources
        )

        print(
            "=" * 50
        )


        # ====================================================
        # RETURN
        # ====================================================

        return {

            "answer": answer,

            "sources": sources
        }


    except HTTPException:

        raise


    except Exception as error:

        print()
        print(
            "========== ASK ERROR =========="
        )

        print(
            type(error).__name__
        )

        print(
            error
        )

        print(
            "==============================="
        )


        raise HTTPException(

            status_code=500,

            detail=str(error)
        )