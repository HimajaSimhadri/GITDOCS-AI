import chromadb
from sentence_transformers import SentenceTransformer


# 1. Read the document
with open("data/sample.txt", "r", encoding="utf-8") as file:
    text = file.read()

print("Document loaded successfully!")
print(text)


# 2. Split the document into chunks
chunks = [
    text[i:i + 300]
    for i in range(0, len(text), 300)
]

print("\nNumber of chunks:", len(chunks))


# 3. Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded!")


# 4. Convert chunks into embeddings
embeddings = model.encode(chunks)

print("Embeddings created!")
print("Number of embeddings:", len(embeddings))


# 5. Create ChromaDB client
client = chromadb.PersistentClient(path="chroma_db")


# 6. Create a collection
collection = client.get_or_create_collection(
    name="gitdocs"
)


# 7. Store chunks and embeddings
collection.add(
    ids=[str(i) for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings.tolist()
)

print("Data stored in ChromaDB successfully!")