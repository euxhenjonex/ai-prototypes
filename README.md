# 🎓 Learn AI with RAG

> An interactive AI Engineering tutor powered by Retrieval Augmented Generation - Learn by asking questions!

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 What is This?

**Learn AI with RAG** is an interactive learning platform where you can ask questions about AI Engineering and get instant, accurate answers powered by Retrieval Augmented Generation (RAG).

Think of it as your **personal AI tutor** that has studied 17 comprehensive lessons and can explain any concept conversationally in English or Italian!

### ✨ Key Features

**For Learners:**
- 💬 **Interactive Q&A** - Ask questions in natural language
- 🌍 **Multilingual** - Responds in English or Italian (auto-detects your language!)
- 📚 **17 Comprehensive Lessons** - From Python basics to production deployment
- 🎓 **Beginner-Friendly** - Complex concepts explained simply
- 📊 **Progress Tracking** - See your learning journey
- 💡 **Example Questions** - Get started quickly with suggested topics

**For Developers:**
- 🏗️ **Production-Ready Stack** - FastAPI + LangChain + FAISS + Streamlit
- 🐳 **Fully Dockerized** - One command to run everything
- ✅ **Comprehensive Tests** - 45+ tests with pytest (97.8% pass rate)
- 🔄 **CI/CD Pipeline** - Automated testing with GitHub Actions
- 📖 **Well-Documented** - Clear code with extensive comments

---

## 📚 What You'll Learn

### Beginner Level
- 🐍 Python Basics for AI (virtual envs, pip, async/await, APIs)
- 🔌 APIs Explained Simply (REST, JSON, HTTP methods)
- 🧠 Neural Networks Introduction (how they work, types, when to use)
- 🤖 LLM Fundamentals (tokens, temperature, prompting)

### Intermediate Level
- 📊 Machine Learning Basics (supervised, unsupervised, reinforcement)
- ⛓️ LangChain Introduction (chains, agents, memory)
- 🔍 RAG Architecture (components, pipeline, advanced techniques)
- 💾 Vector Databases (FAISS, Pinecone, Chroma, Weaviate)
- 🧮 Embeddings & Semantic Search
- 🚀 Building Your First RAG System (step-by-step tutorial)

### Advanced Level
- 💬 Prompt Engineering (techniques, patterns, best practices)
- ⚙️ LLM Production Best Practices (error handling, monitoring, security)
- ⚡ FastAPI Development (API design, testing, deployment)
- 🐳 Docker Containerization (multi-stage builds, optimization)
- ✅ Testing Best Practices (unit, integration, E2E tests)
- 🔄 CI/CD with GitHub Actions (workflows, automation)

**Total:** ~150KB of curated educational content!

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed ([Get Docker](https://www.docker.com/get-started))
- OpenAI API key ([Get API Key](https://platform.openai.com/api-keys))

### Run with Docker Compose (Recommended - 2 minutes)

1. **Clone the repository**
   ```bash
   git clone https://github.com/euxhenjonex/learn-ai-with-rag.git
   cd learn-ai-with-rag
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Open the app**
   - 🎓 **Frontend (Streamlit):** http://localhost:8501
   - 📖 **API Docs:** http://localhost:8000/docs

That's it! Start asking questions and learning! 🎉

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│   Streamlit     │────────▶│   FastAPI        │
│   Frontend      │  HTTP   │   Backend        │
│   (Port 8501)   │         │   (Port 8000)    │
│                 │         │                  │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   LangChain      │
                            │   + FAISS        │
                            │   Vector Store   │
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   OpenAI         │
                            │   GPT-4o-mini    │
                            └──────────────────┘
```

### How It Works

1. **You ask a question** via Streamlit frontend (in English or Italian)
2. **Frontend sends request** to FastAPI backend
3. **LangChain retrieves** relevant lesson content from FAISS vector store
4. **OpenAI generates answer** based on retrieved context (in your language!)
5. **Answer is displayed** to you with related topics

---

## 💻 Local Development (Without Docker)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY=your_key_here

# Run API
uvicorn main:app --reload
```

Visit: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set API URL
export API_URL=http://localhost:8000

# Run Streamlit
streamlit run app.py
```

Visit: http://localhost:8501

### Run Tests

```bash
cd backend
pytest -v

# With coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

---

## 📖 Example Interactions

**Q:** "Che cos'è il RAG?" (Italian question)

**A:** "Il RAG (Retrieval Augmented Generation) è una tecnica che migliora i Large Language Models combinandoli con sistemi di recupero di conoscenza esterna. È utile perché fornisce informazioni aggiornate, consente l'accesso a conoscenze specifiche del dominio, riduce le allucinazioni..." (Italian response)

---

**Q:** "What's the difference between FAISS and Pinecone?"

**A:** "FAISS (Facebook AI Similarity Search) is a library for local development, excellent for prototyping and small-medium datasets. It's free and open-source but requires manual management. Pinecone is a managed cloud service that scales to billions of vectors and handles infrastructure for you..."

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend API | FastAPI | REST API endpoints |
| LLM Framework | LangChain | RAG orchestration |
| Vector Store | FAISS | Semantic search |
| LLM | OpenAI GPT-4o-mini | Answer generation |
| Frontend | Streamlit | Interactive UI |
| Testing | pytest | Test automation |
| Containerization | Docker | Deployment |
| Orchestration | Docker Compose | Multi-container management |
| CI/CD | GitHub Actions | Automation |

---

## 📁 Project Structure

```
learn-ai-with-rag/
├── backend/                  # FastAPI backend
│   ├── main.py              # API with multilingual RAG
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/               # 45+ tests
├── content/
│   └── lessons/             # 17 comprehensive lessons
│       ├── 00_python_basics_for_ai.txt
│       ├── 01_machine_learning_basics.txt
│       ├── ...
│       └── 15_building_first_rag_system.txt
├── frontend/                # Streamlit frontend
│   ├── app.py              # Interactive tutor UI
│   ├── requirements.txt
│   └── Dockerfile
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md
│   └── LESSON_CATALOG.md
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
├── docker-compose.yml      # Orchestration
├── .env.example            # Environment template
└── README.md               # This file
```

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest -v

# Run only unit tests
pytest -v -m "not integration"

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Test Results:
# 45 passing / 46 total (97.8% pass rate)
# Execution time: ~0.07 seconds
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Add new lessons** - Create `.txt` files in `content/lessons/`
2. **Improve existing content** - Fix typos, add examples, clarify concepts
3. **Add features** - New UI components, better UX, additional functionality
4. **Report bugs** - Open an issue with details

---

## 🎯 Why This Project?

I built this to solve a problem I personally had: learning AI Engineering was fragmented across docs, blogs, and courses. This tutor consolidates everything in one interactive experience.

**What makes it special:**
- ✅ **Learn by doing** - Ask questions, get answers instantly
- ✅ **Comprehensive** - Covers everything from basics to production deployment
- ✅ **Production-ready** - Not just a demo, but a real application
- ✅ **Multilingual** - English and Italian support built-in
- ✅ **Beginner-friendly** - Complex topics explained simply
- ✅ **Open source** - Learn from the code too!

---

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| Total Files Created | 25+ |
| Lines of Code | 1,500+ |
| Test Coverage | 97.8% |
| Docker Image Size (Backend) | 620MB |
| Content Size | ~150KB |
| Lessons | 17 |
| Languages Supported | 2 (EN, IT) |

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Euxhenjo Nexhipi**

- GitHub: [@euxhenjonex](https://github.com/euxhenjonex)
- LinkedIn: [Connect with me](https://linkedin.com/in/euxhenjonex)

---

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [OpenAI](https://openai.com)
- UI with [Streamlit](https://streamlit.io)
- Vector search with [FAISS](https://github.com/facebookresearch/faiss)
- API framework by [FastAPI](https://fastapi.tiangolo.com)

---

## ⭐ Star History

If you find this project helpful, please consider giving it a star! ⭐

---

<div align="center">
  <h3>🎓 Start Learning Today!</h3>
  <p>Made with ❤️ for the AI Engineering community</p>
  <p><a href="https://github.com/euxhenjonex/learn-ai-with-rag">🌟 Star on GitHub</a> • <a href="https://github.com/euxhenjonex/learn-ai-with-rag/issues">🐛 Report Bug</a> • <a href="https://github.com/euxhenjonex/learn-ai-with-rag/issues">💡 Request Feature</a></p>
</div>
