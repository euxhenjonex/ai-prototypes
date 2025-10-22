"""
LangChain Mini-RAG API

A FastAPI application that implements Retrieval Augmented Generation (RAG)
using LangChain, FAISS vector store, and OpenAI embeddings.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import os

# LangChain imports
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# --- Configuration ---
class Config:
    """Application configuration"""
    BASE_DIR = Path(__file__).resolve().parent
    ENV_PATH = BASE_DIR / ".env"
    DATA_PATH = BASE_DIR / "sample_data"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    RETRIEVER_K = 3
    LLM_MODEL = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.5

# Load environment variables
load_dotenv(dotenv_path=Config.ENV_PATH)

# --- Utility Functions ---
def get_api_key() -> str:
    """
    Get OpenAI API key from environment.

    Returns:
        str: OpenAI API key

    Raises:
        ValueError: If API key is not found
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        raise ValueError("OPENAI_API_KEY not found. Check your .env file.")
    logger.info("API key loaded successfully")
    return api_key

def load_documents(data_path: Path) -> List[Document]:
    """
    Load and process all text documents from the data directory.

    Args:
        data_path: Path to directory containing text files

    Returns:
        List of Document objects

    Raises:
        FileNotFoundError: If data path doesn't exist
        ValueError: If no documents found
    """
    if not data_path.exists():
        logger.error(f"Data path does not exist: {data_path}")
        raise FileNotFoundError(f"Data directory not found: {data_path}")

    # Find all .txt files
    txt_files = list(data_path.glob("*.txt"))
    if not txt_files:
        logger.error(f"No .txt files found in {data_path}")
        raise ValueError(f"No text files found in {data_path}")

    logger.info(f"Found {len(txt_files)} text files")

    # Load all documents
    all_text = []
    for txt_file in txt_files:
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:  # Only add non-empty files
                    all_text.append(content)
                    logger.info(f"Loaded: {txt_file.name} ({len(content)} chars)")
        except Exception as e:
            logger.warning(f"Failed to load {txt_file.name}: {e}")
            continue

    if not all_text:
        raise ValueError("No content loaded from text files")

    # Combine all text
    combined_text = "\n\n".join(all_text)
    logger.info(f"Total content: {len(combined_text)} characters")

    # Split into chunks
    splitter = CharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    chunks = splitter.split_text(combined_text)

    # Handle edge case: no chunks
    if not chunks:
        chunks = [combined_text]

    logger.info(f"Created {len(chunks)} chunks")

    # Convert to Document objects
    docs = [Document(page_content=chunk) for chunk in chunks]
    return docs

def create_vectorstore(
    documents: List[Document],
    api_key: str
) -> FAISS:
    """
    Create FAISS vector store from documents.

    Args:
        documents: List of Document objects
        api_key: OpenAI API key

    Returns:
        FAISS vector store

    Raises:
        ValueError: If documents list is empty
    """
    if not documents:
        logger.error("No documents provided for vectorstore creation")
        raise ValueError("Cannot create vectorstore from empty document list")

    logger.info(f"Creating embeddings for {len(documents)} documents...")
    embeddings = OpenAIEmbeddings(api_key=api_key)

    vectorstore = FAISS.from_documents(documents, embeddings)
    logger.info("Vector store created successfully")

    return vectorstore

def format_docs(docs: List[Document]) -> str:
    """
    Format list of documents into a single string.

    Args:
        docs: List of Document objects

    Returns:
        Formatted string with document contents
    """
    return "\n\n".join(doc.page_content for doc in docs)

# --- Initialize Application Components ---
# These will be initialized at startup
api_key = None
documents = None
vectorstore = None
retriever = None
llm = None
qa_chain = None


def initialize_app():
    """
    Initialize the application components.

    This function is called at startup to initialize:
    - API key
    - Document loading
    - Vector store
    - LLM and QA chain

    Separating initialization allows for better testing and lazy loading.
    """
    global api_key, documents, vectorstore, retriever, llm, qa_chain

    logger.info("Initializing LangChain Mini-RAG API...")

    # Get API key
    api_key = get_api_key()

    # Load documents
    documents = load_documents(Config.DATA_PATH)

    # Create vector store
    vectorstore = create_vectorstore(documents, api_key)
    retriever = vectorstore.as_retriever(search_kwargs={"k": Config.RETRIEVER_K})

    # Build QA chain
    llm = ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=Config.LLM_TEMPERATURE,
        api_key=api_key
    )

    # Create prompt template
    template = """Answer the question based only on the following context:
{context}

Question: {question}

Provide a comprehensive answer based on the context above. If the context doesn't contain enough information to answer the question, say so.

Answer:"""
    prompt = ChatPromptTemplate.from_template(template)

    # Build the chain using LCEL
    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logger.info("QA chain initialized successfully")

# --- FastAPI Application ---
app = FastAPI(
    title="LangChain Mini-RAG API",
    description="A Retrieval Augmented Generation API powered by LangChain, FAISS, and OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class QueryInput(BaseModel):
    """Input model for query endpoint"""
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The question to ask the knowledge base",
        example="What is Artificial Intelligence?"
    )

    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or only whitespace')
        return v.strip()

class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="The generated answer")

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="API status")
    message: str = Field(..., description="Status message")
    documents_loaded: int = Field(..., description="Number of documents in knowledge base")

# --- API Endpoints ---
@app.get(
    "/",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and get basic information"
)
async def root():
    """
    Health check endpoint.

    Returns basic information about the API status and loaded documents.
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        message="LangChain Mini-RAG API is running 🚀",
        documents_loaded=len(documents) if documents else 0
    )

@app.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query Knowledge Base",
    description="Ask a question and get an answer based on the knowledge base"
)
async def query_docs(input_data: QueryInput) -> QueryResponse:
    """
    Query the knowledge base with a question.

    Args:
        input_data: QueryInput containing the question

    Returns:
        QueryResponse with the question and generated answer

    Raises:
        HTTPException: If an error occurs during query processing
    """
    logger.info(f"Query received: {input_data.question[:100]}...")

    try:
        # Invoke the QA chain
        answer = qa_chain.invoke(input_data.question)

        logger.info(f"Answer generated successfully ({len(answer)} chars)")

        return QueryResponse(
            question=input_data.question,
            answer=answer
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your query: {str(e)}"
        )

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Detailed Health Check",
    description="Get detailed health information about the API"
)
async def health_check():
    """
    Detailed health check endpoint.

    Returns comprehensive information about API status.
    """
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        documents_loaded=len(documents) if documents else 0
    )

# --- Application Startup/Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize and log application startup"""
    # Initialize the application components
    initialize_app()

    logger.info("=" * 50)
    logger.info("LangChain Mini-RAG API started successfully")
    logger.info(f"Documents loaded: {len(documents) if documents else 0}")
    logger.info(f"Model: {Config.LLM_MODEL}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("LangChain Mini-RAG API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
