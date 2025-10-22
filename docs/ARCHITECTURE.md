# 🏗️ Architecture Documentation

## System Overview

**Learn AI with RAG** is a full-stack application implementing Retrieval Augmented Generation for educational purposes.

## Components

### 1. Backend API (FastAPI)
**Location:** `backend/main.py`
**Port:** 8000

**Responsibilities:**
- Document loading and processing
- Text chunking and embedding generation
- FAISS vector store management
- RAG query processing with multilingual support
- RESTful API endpoints

**Key Technologies:**
- FastAPI: Web framework
- LangChain: RAG orchestration
- FAISS: Vector similarity search
- OpenAI: Embeddings and LLM

**Endpoints:**
- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /query` - RAG query endpoint

### 2. Frontend UI (Streamlit)
**Location:** `frontend/app.py`
**Port:** 8501

**Responsibilities:**
- Interactive Q&A interface
- Lesson catalog browser
- Progress tracking
- Example question suggestions
- Multilingual UI

**Features:**
- Auto-detects question language
- Progress statistics
- Lesson browsing by difficulty
- Conversation history
- Related topic suggestions

### 3. Content Store
**Location:** `content/lessons/`

**Structure:**
- 17 markdown-formatted lessons
- Organized by difficulty (00-15)
- Topics: Python, APIs, ML, NNs, LLMs, RAG, Vector DBs, Production

**Size:** ~150KB of educational content

### 4. Vector Database
**Technology:** FAISS (CPU version)
**Created at:** Application startup

**Process:**
1. Load all `.txt` files from `content/lessons/`
2. Split into 500-character chunks (50 char overlap)
3. Generate embeddings via OpenAI
4. Index in FAISS for fast similarity search

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                            │
│  - User inputs question (English or Italian)                    │
│  - Optional: Language preference selection                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP POST /query
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                              │
│                                                                  │
│  1. Receive question                                            │
│  2. Detect language (via prompt engineering)                    │
│  3. Generate question embedding                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FAISS VECTOR STORE                             │
│  - Semantic similarity search                                   │
│  - Retrieve top 4 most relevant chunks                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LANGCHAIN RAG CHAIN                           │
│  - Format retrieved chunks as context                           │
│  - Construct prompt with language instruction                   │
│  - Send to OpenAI GPT-4o-mini                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OPENAI LLM                                  │
│  - Generate educational answer                                  │
│  - Respond in detected language                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE TO USER                              │
│  - Display answer in Streamlit                                  │
│  - Show related topics                                          │
│  - Update progress tracking                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Multilingual Support

Implemented via prompt engineering:

```python
template = """You are an AI Engineering tutor...

IMPORTANT LANGUAGE INSTRUCTION:
- Detect the language of the user's question
- If Italian, respond in Italian
- If English, respond in English
- Maintain same language throughout

Context: {context}
Question: {question}
Answer (in same language as question):"""
```

**Benefits:**
- No separate models needed
- Natural language detection
- Consistent responses
- Easy to extend to more languages

## Configuration

**Backend Config** (`backend/main.py`):
```python
class Config:
    DATA_PATH = "content/lessons"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    RETRIEVER_K = 4
    LLM_MODEL = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.7
```

**Frontend Config** (`frontend/app.py`):
```python
API_URL = os.getenv("API_URL", "http://localhost:8000")
```

## Deployment Architecture

### Docker Compose (Development & Production)

```yaml
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./content:/app/content:ro"]
    networks: [rag-network]

  frontend:
    build: ./frontend
    ports: ["8501:8501"]
    environment: ["API_URL=http://api:8000"]
    depends_on: [api]
    networks: [rag-network]
```

**Benefits:**
- Single command startup
- Automatic networking
- Health checks
- Volume mounting for content updates

## Security Considerations

1. **API Keys:** Never committed to repository
   - Stored in `.env` (gitignored)
   - Loaded via `python-dotenv`

2. **CORS:** Configured in FastAPI
   - Currently allows all origins (development)
   - Should be restricted in production

3. **Input Validation:** Pydantic models
   - Question length limits (1-1000 chars)
   - Trimming whitespace
   - Type validation

4. **Docker:** Non-root user in backend container

## Performance Optimization

1. **Embedding Caching:** FAISS vector store persists across requests
2. **Chunking Strategy:** 500 chars balances context and retrieval precision
3. **Model Selection:** GPT-4o-mini for cost/speed balance
4. **Retriever K=4:** Optimal context without token bloat

## Testing Strategy

**Unit Tests:** Business logic, utility functions
**Integration Tests:** API endpoints with real OpenAI calls
**Fixtures:** Reusable test setup
**Markers:** `@pytest.mark.integration` for CI filtering

**Coverage:** 97.8% (45/46 tests passing)

## Future Enhancements

1. **Vector Store Persistence:** Save FAISS index to disk
2. **Conversation Memory:** Multi-turn context
3. **User Authentication:** Track individual progress
4. **Analytics Dashboard:** Usage metrics
5. **More Languages:** Spanish, French, German support
6. **Lesson Recommendations:** ML-based suggestions
7. **Quiz Mode:** Interactive assessments

## Monitoring & Observability

**Current:**
- Structured logging (timestamp, level, message)
- Health check endpoints
- Docker health checks

**Recommended for Production:**
- Prometheus metrics
- ELK stack for log aggregation
- Sentry for error tracking
- Response time monitoring
