from sentence_transformers import SentenceTransformer
import chromadb

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("gitdocs")

question = "What frontend technology is being used?"

embedding = model.encode(question).tolist()

results = collection.query(
    query_embeddings=[embedding],
    n_results=3
)

print("\n========== RETRIEVED DOCUMENTS ==========\n")

for i, document in enumerate(results["documents"][0]):
    print(f"DOCUMENT {i + 1}:")
    print(document)
    print("\n----------------------------------------\n")