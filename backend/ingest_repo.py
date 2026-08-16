import chromadb
from sentence_transformers import SentenceTransformer

from repo_reader import read_repository


# -----------------------------
# Configuration
# -----------------------------

REPO_PATH = "repositories/Online-Exam-Portall"

CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "gitdocs_repo"


# -----------------------------
# Load embedding model
# -----------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------
# Connect to ChromaDB
# -----------------------------

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# Delete old collection if it exists
try:
    client.delete_collection(
        name=COLLECTION_NAME
)
except Exception:
    pass


collection = client.create_collection(
    name=COLLECTION_NAME
)


# -----------------------------
# Read repository
# -----------------------------

print("Reading repository files...")

documents = read_repository(
    REPO_PATH
)

print(
    f"Found {len(documents)} files."
)


# -----------------------------
# Create chunks
# -----------------------------

chunks = []
metadatas = []


for document in documents:

    file_path = document["path"]
    content = document["content"]

    # Simple character-based chunks
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


print(
    f"Created {len(chunks)} chunks."
)


# -----------------------------
# Create embeddings
# -----------------------------

print("Creating embeddings...")

embeddings = embedding_model.encode(
    chunks,
    show_progress_bar=True
).tolist()


# -----------------------------
# Store in ChromaDB
# -----------------------------

print("Storing in ChromaDB...")


ids = [
    f"chunk-{i}"
    for i in range(len(chunks))
]


collection.add(
    ids=ids,
    documents=chunks,
    embeddings=embeddings,
    metadatas=metadatas
)


print("\n================================")
print("Repository ingestion complete!")
print("================================")

print(
    "Files:",
    len(documents)
)

print(
    "Chunks:",
    len(chunks)
)

print(
    "ChromaDB documents:",
    collection.count()
)