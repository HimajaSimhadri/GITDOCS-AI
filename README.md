\# GitDocs-AI 🤖



GitDocs-AI is an AI-powered developer assistant that allows users to connect a GitHub repository and ask questions about its codebase using \*\*Retrieval-Augmented Generation (RAG)\*\*.



Instead of manually searching through multiple files, GitDocs-AI retrieves the most relevant parts of the repository and uses them to generate context-aware answers.



\## 🚀 Features



\* 🔗 Load a GitHub repository

\* 📂 Read and process repository files

\* ✂️ Split source code into manageable chunks

\* 🧠 Generate semantic embeddings

\* 🗄️ Store embeddings using ChromaDB

\* 🔎 Retrieve relevant code based on user queries

\* 💬 Ask questions about a repository using natural language

\* 🌐 Web-based frontend interface

\* 🔐 Environment variables for API credentials



\## 🏗️ Architecture



```text

&#x20;                   GitHub Repository

&#x20;                          │

&#x20;                          ▼

&#x20;                   GitHub Loader

&#x20;                          │

&#x20;                          ▼

&#x20;                   Repository Reader

&#x20;                          │

&#x20;                          ▼

&#x20;                    Text Chunking

&#x20;                          │

&#x20;                          ▼

&#x20;                Sentence Transformer

&#x20;                     Embeddings

&#x20;                          │

&#x20;                          ▼

&#x20;                      ChromaDB

&#x20;                   Vector Database

&#x20;                          │

&#x20;                          ▼

&#x20;                    User Question

&#x20;                          │

&#x20;                          ▼

&#x20;                 Similarity Retrieval

&#x20;                          │

&#x20;                          ▼

&#x20;                  Relevant Code Chunks

&#x20;                          │

&#x20;                          ▼

&#x20;                        LLM

&#x20;                          │

&#x20;                          ▼

&#x20;                   AI Generated Answer

```



\## 🛠️ Tech Stack



\### Backend



\* Python

\* ChromaDB

\* Sentence Transformers

\* GitHub Repository Integration

\* REST API



\### Frontend



\* React.js

\* JavaScript

\* CSS



\### AI / RAG



\* Retrieval-Augmented Generation (RAG)

\* Text Embeddings

\* Vector Similarity Search

\* ChromaDB Vector Store



\## 📁 Project Structure



```text

GITDOCS-AI/

│

├── backend/

│   ├── main.py

│   ├── github\_loader.py

│   ├── repo\_reader.py

│   ├── ingest\_repo.py

│   ├── index\_repository.py

│   ├── test\_github.py

│   └── test\_reader.py

│

├── frontend/

│   └── src/

│       ├── App.jsx

│       └── App.css

│

├── .gitignore

├── .env.example

└── README.md

```



\## ⚙️ How It Works



\### 1. Repository Loading



The user provides a GitHub repository URL.



GitDocs-AI clones the repository locally and prepares it for processing.



\### 2. Repository Reading



The application scans the repository and extracts relevant source files while ignoring unnecessary files.



\### 3. Chunking



Large source files are divided into smaller chunks.



This makes it possible to retrieve only the sections that are relevant to a user's question.



\### 4. Embedding Generation



Each chunk is converted into a numerical vector using a Sentence Transformer model.



These vectors represent the semantic meaning of the code and documentation.



\### 5. Vector Storage



The generated embeddings are stored in \*\*ChromaDB\*\*, which acts as the vector database.



\### 6. Retrieval



When a user asks a question, the question is converted into an embedding.



GitDocs-AI searches ChromaDB for the most semantically similar code chunks.



\### 7. AI Response



The retrieved context is provided to the language model, allowing it to generate an answer based on the actual repository content.



\## 💻 Installation



\### Clone the repository



```bash

git clone https://github.com/HimajaSimhadri/GITDOCS-AI.git

cd GITDOCS-AI

```



\### Create a virtual environment



```bash

python -m venv venv

```



Activate it on Windows:



```powershell

venv\\Scripts\\activate

```



\### Install backend dependencies



```bash

pip install -r backend/requirements.txt

```



\## 🔐 Environment Variables



Create a `.env` file inside the backend directory:



```text

backend/.env

```



Add your required API credentials:



```text

GCP\_API\_KEY=your\_api\_key\_here

```



\*\*Never commit your `.env` file to GitHub.\*\*



The project uses `.gitignore` to prevent environment files and generated data from being committed.



\## ▶️ Running the Project



\### Start the backend



From the project root:



```bash

python backend/main.py

```



\### Start the frontend



Navigate to the frontend directory:



```bash

cd frontend

```



Install dependencies:



```bash

npm install

```



Start the development server:



```bash

npm run dev

```



Then open the local URL shown by the frontend development server.



\## 🧪 Testing



The backend contains test scripts for repository loading and reading:



```bash

python backend/test\_github.py

```



```bash

python backend/test\_reader.py

```



\## 🎯 Why This Project?



Large software repositories can contain hundreds or thousands of files, making it difficult for developers to quickly understand an unfamiliar codebase.



GitDocs-AI solves this problem by combining:



\*\*GitHub + Embeddings + Vector Search + RAG + LLMs\*\*



This allows developers to interact with a codebase using natural language instead of manually searching through files.



\## 🔮 Future Improvements



\* Support multiple GitHub repositories

\* Add authentication

\* Improve code-aware chunking

\* Add conversation history

\* Support repository documentation generation

\* Add code explanation and debugging modes

\* Improve retrieval using hybrid search

\* Deploy the application to the cloud

\* Add CI/CD pipeline

\* Add support for private repositories



\## 👩‍💻 Author



\*\*Himaja Simhadri\*\*



GitHub: \[HimajaSimhadri](https://github.com/HimajaSimhadri)



\## ⭐ Project



If you find this project useful, consider giving it a ⭐ on GitHub.



