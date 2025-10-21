from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from pathlib import Path

# ✅ LangChain (versione compatibile)
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate






# --- Load environment ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")

# --- Initialize app ---
app = FastAPI(title="LangChain Mini-RAG API")

# --- Prepare data ---
DATA_PATH = Path(__file__).resolve().parent / "sample_data" / "intro-ai.txt"

if not DATA_PATH.exists():
    raise FileNotFoundError("intro-ai.txt not found in sample_data/")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    text = f.read()

splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)

# Se non ci sono chunk, usa il testo intero
if not chunks:
    chunks = [text]

docs = [Document(page_content=chunk) for chunk in chunks]

# --- Create vectorstore ---
embeddings = OpenAIEmbeddings(api_key=api_key)

# Controlla che ci siano documenti
if not docs:
    raise ValueError("No documents to index. Check your sample_data file.")

vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# --- Build QA chain ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=api_key)

# Create a prompt template
template = """Answer the question based only on the following context:
{context}

Question: {question}

Answer:"""
prompt = ChatPromptTemplate.from_template(template)

# Helper function to format docs
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Build the chain using LCEL
qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)



# --- API models ---
class QueryInput(BaseModel):
    question: str

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "LangChain Mini-RAG API is running 🚀"}

@app.post("/query")
async def query_docs(input_data: QueryInput):
    """Ask a question based on the local knowledge base."""
    try:
        answer = qa_chain.invoke(input_data.question)
        return {
            "question": input_data.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
