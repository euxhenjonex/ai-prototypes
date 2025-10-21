# 🚀 LangChain Mini-RAG API

A minimal **Retrieval-Augmented Generation (RAG)** API built with **FastAPI**, **LangChain**, and **OpenAI**.  
This project demonstrates how to connect a local knowledge base (FAISS vector store) with an OpenAI model to answer questions contextually.

---

## 🧠 Overview

This prototype is part of a collection of **AI Engineering demos**, showing practical use cases of language models and vector databases.

The goal is to build a **lightweight RAG pipeline** — from document ingestion to semantic search and contextual response generation — fully operational through a simple REST API.

---

## ⚙️ Tech Stack

- 🧩 **FastAPI** — modern Python framework for building APIs  
- 🧠 **LangChain** — handles the RAG logic and document pipelines  
- 🔍 **FAISS** — local vector database for semantic similarity search  
- 🤖 **OpenAI API** — LLM reasoning and text generation  
- 🔑 **python-dotenv** — for secure API key management  

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|:--------|:----------|:-------------|
| `GET` | `/` | Health check |
| `POST` | `/query` | Query your local knowledge base |

---

## 🧪 Example Request

```json
{
  "question": "What is Artificial Intelligence?"
}
```

### Example Response
```json
{
  "question": "What is Artificial Intelligence?",
  "answer": "Artificial Intelligence is the field focused on creating machines capable of human-like reasoning and learning."
}
```

🚀 Run Locally
1️⃣ Clone the repository
git clone https://github.com/euxhenjonex/ai-prototypes.git
cd ai-prototypes/02-langchain-rag

2️⃣ Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ **Set your OpenAI API key**

Create a `.env` file in the project root:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5️⃣ **Run the API**
```bash
uvicorn main:app --reload
```

Then open:  
👉 **http://127.0.0.1:8000/docs** (or whatever port is available)

---

## 🧱 How It Works

1. **Document loading** — reads text files from `sample_data/`
2. **Chunking & Embedding** — splits text and converts it into vector embeddings
3. **FAISS Indexing** — stores embeddings for semantic retrieval
4. **LLM Querying** — combines user question + retrieved context to generate an informed answer

---