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

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

gemini_client = genai.Client(
    api_key=api_key
)


# ============================================================
# CHROMADB
# ============================================================

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "gitdocs"

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


try:

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    print(
        f"ChromaDB collection loaded: {COLLECTION_NAME}"
    )

except Exception:

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME
    )

    print(
        f"ChromaDB collection created: {COLLECTION_NAME}"
    )


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="GitDocs AI",
    description="RAG-powered GitHub Repository Assistant"
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
def index_github_repository(
    data: RepositoryRequest
):

    print()
    print("=" * 50)
    print("INDEXING REPOSITORY")
    print(
        f"URL: {data.url}"
    )
    print("=" * 50)

    try:

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
        print(
            "INDEX ERROR:",
            str(error)
        )

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
    print("=" * 50)
    print("NEW QUESTION")
    print(
        f"Question: {question}"
    )
    print("=" * 50)


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
        # LOAD TF-IDF VECTORIZER
        # ====================================================

        vectorizer_path = os.path.join(

            CHROMA_PATH,

            "vectorizer.pkl"

        )


        print(
            "Loading TF-IDF vectorizer..."
        )


        if not os.path.exists(
            vectorizer_path
        ):

            raise ValueError(
                "No indexed repository found. "
                "Please index a GitHub repository first."
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


        question_matrix = (
            vectorizer.transform(
                [question]
            )
        )


        question_vector = (
            question_matrix
            .toarray()
            .tolist()[0]
        )


        print(
            "Question vector created."
        )

        print(
            f"Vector dimensions: "
            f"{len(question_vector)}"
        )


        # ====================================================
        # CHECK CHROMADB
        # ====================================================

        print(
            f"Chroma collection: "
            f"{COLLECTION_NAME}"
        )


        collection_count = (
            collection.count()
        )


        print(
            f"Documents in Chroma: "
            f"{collection_count}"
        )


        if collection_count == 0:

            raise ValueError(
                "ChromaDB is empty. "
                "Please index a repository first."
            )


        # ====================================================
        # SEARCH CHROMADB
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
            )

        )


        # ====================================================
        # CHECK RESULTS
        # ====================================================

        documents = results.get(
            "documents",
            [[]]
        )

        metadatas = results.get(
            "metadatas",
            [[]]
        )


        if not documents or not documents[0]:

            raise ValueError(
                "No relevant repository content "
                "was found for this question."
            )


        documents = documents[0]


        if metadatas and metadatas[0]:

            metadatas = metadatas[0]

        else:

            metadatas = []


        print()
        print(
            "========== CHROMA RESULTS =========="
        )

        print(
            f"Results returned: "
            f"{len(documents)}"
        )


        # ====================================================
        # BUILD CONTEXT
        # ====================================================

        context_parts = []

        sources = []


        for index, document in enumerate(
            documents
        ):

            # -----------------------------------------------
            # Metadata
            # -----------------------------------------------

            if index < len(metadatas):

                metadata = metadatas[index]

                file_name = metadata.get(
                    "file",
                    "Unknown file"
                )

            else:

                file_name = "Unknown file"


            # -----------------------------------------------
            # Sources
            # -----------------------------------------------

            if file_name not in sources:

                sources.append(
                    file_name
                )


            # -----------------------------------------------
            # Debug output
            # -----------------------------------------------

            print()
            print(
                f"--- RESULT {index + 1} ---"
            )

            print(
                f"FILE: {file_name}"
            )


            # -----------------------------------------------
            # Context
            # -----------------------------------------------

            context_parts.append(

                f"FILE: {file_name}\n\n"
                f"{document}"

            )


        context = "\n\n".join(
            context_parts
        )


        # ====================================================
        # LIMIT CONTEXT
        # ====================================================

        # Prevent extremely large prompts.

        MAX_CONTEXT_LENGTH = 12000


        if len(context) > MAX_CONTEXT_LENGTH:

            context = context[
                :MAX_CONTEXT_LENGTH
            ]


        # ====================================================
        # GEMINI PROMPT
        # ====================================================

        prompt = f"""
You are GitDocs AI.

You are an AI assistant that answers questions
about a software repository.

You MUST use the repository context below.

IMPORTANT RULES:

1. Use only the repository context.
2. Do not invent information.
3. Answer clearly and directly.
4. If the answer exists in the context,
   explain it accurately.
5. Mention relevant source files.
6. If the answer cannot be determined from
   the context, say:

   "I could not find this information
   in the indexed repository."

7. Do not claim that something exists in the
   repository unless the context supports it.

REPOSITORY CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""


        # ====================================================
        # GEMINI
        # ====================================================

        print()
        print(
            "Sending context to Gemini..."
        )


        response = None


        # ----------------------------------------------------
        # ONLY TWO ATTEMPTS
        # ----------------------------------------------------

        for attempt in range(2):

            try:

                print(
                    f"Gemini attempt "
                    f"{attempt + 1}/2"
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


                print()
                print(
                    "Gemini ERROR:"
                )

                print(
                    error_message
                )


                # --------------------------------------------
                # Retry once
                # --------------------------------------------

                if attempt == 0:

                    print(
                        "Gemini temporarily unavailable."
                    )

                    print(
                        "Waiting 2 seconds before retry..."
                    )

                    time.sleep(2)


                else:

                    # ----------------------------------------
                    # Final failure
                    # ----------------------------------------

                    if (
                        "503" in error_message
                        or
                        "UNAVAILABLE"
                        in error_message
                    ):

                        raise HTTPException(

                            status_code=503,

                            detail=(
                                "Gemini is temporarily "
                                "unavailable. Please try "
                                "the question again."
                            )

                        )


                    raise HTTPException(

                        status_code=500,

                        detail=(
                            "Gemini error: "
                            + error_message
                        )

                    )


        # ====================================================
        # CHECK RESPONSE
        # ====================================================

        if response is None:

            raise HTTPException(

                status_code=503,

                detail=(
                    "Gemini did not return a response."
                )

            )


        answer = response.text


        if not answer:

            raise HTTPException(

                status_code=500,

                detail=(
                    "Gemini returned an empty answer."
                )

            )


        # ====================================================
        # SUCCESS
        # ====================================================

        print()
        print(
            "Answer generated successfully."
        )

        print(
            f"Sources: {sources}"
        )

        print(
            "=" * 50
        )


        return {

            "answer": answer,

            "sources": sources

        }


    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except HTTPException:

        raise


    except Exception as error:

        print()
        print(
            "ASK ERROR:"
        )

        print(
            str(error)
        )

        print(
            "=" * 50
        )


        raise HTTPException(

            status_code=500,

            detail=str(error)

        )