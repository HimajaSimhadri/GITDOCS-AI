import os

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai


# 1. Load API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

# 2. Connect to Gemini
gemini_client = genai.Client(api_key=api_key)

# 3. Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 4. Connect to ChromaDB
chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = chroma_client.get_collection(
    name="gitdocs"
)

# 5. Ask question
question = input("\nAsk a question: ")

# 6. Convert question into embedding
question_embedding = embedding_model.encode(
    question
).tolist()

# 7. Search ChromaDB
results = collection.query(
    query_embeddings=[question_embedding],
    n_results=3
)

# 8. Get retrieved documents
documents = results["documents"][0]

# 9. Combine retrieved chunks
context = "\n\n".join(documents)

# 10. Create RAG prompt
prompt = f"""
You are GitDocs AI, an AI assistant that answers questions
about a software repository.

Use ONLY the context provided below.

If the answer cannot be found in the context,
say:

"I couldn't find that information in the repository."

Context:
{context}

Question:
{question}

Give a clear and concise answer.
"""

# 11. Send context to Gemini
response = gemini_client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

# 12. Display answer
print("\n==============================")
print("        GitDocs AI 🤖")
print("==============================")

print(response.text)