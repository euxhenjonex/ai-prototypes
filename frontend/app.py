"""
Learn AI with RAG - Interactive AI Tutor Frontend

A beginner-friendly Streamlit interface for learning AI Engineering concepts
through an interactive tutor powered by RAG.
"""

import streamlit as st
import requests
import os
from typing import Optional, List, Dict
import json

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Lesson catalog with metadata
LESSONS = {
    "Beginner": [
        {"id": "00", "title": "Python Basics for AI", "emoji": "🐍", "topics": "Virtual envs, pip, async/await, APIs"},
        {"id": "12", "title": "APIs Explained Simply", "emoji": "🔌", "topics": "REST, JSON, HTTP methods"},
        {"id": "13", "title": "Neural Networks Intro", "emoji": "🧠", "topics": "How they work, types, when to use"},
        {"id": "14", "title": "LLM Fundamentals", "emoji": "🤖", "topics": "Tokens, temperature, prompting"},
    ],
    "Intermediate": [
        {"id": "01", "title": "Machine Learning Basics", "emoji": "📊", "topics": "Supervised, unsupervised, reinforcement"},
        {"id": "02", "title": "LangChain Introduction", "emoji": "⛓️", "topics": "Chains, agents, memory"},
        {"id": "03", "title": "RAG Architecture", "emoji": "🔍", "topics": "Components, pipeline, techniques"},
        {"id": "04", "title": "Vector Databases", "emoji": "💾", "topics": "FAISS, Pinecone, Chroma"},
        {"id": "05", "title": "Embeddings & Semantic Search", "emoji": "🧮", "topics": "Word2Vec, BERT, similarity"},
        {"id": "15", "title": "Building Your First RAG System", "emoji": "🚀", "topics": "Step-by-step tutorial"},
    ],
    "Advanced": [
        {"id": "06", "title": "Prompt Engineering", "emoji": "💬", "topics": "Techniques, patterns, best practices"},
        {"id": "07", "title": "LLM Production Best Practices", "emoji": "⚙️", "topics": "Error handling, monitoring, security"},
        {"id": "08", "title": "FastAPI Development", "emoji": "⚡", "topics": "API design, testing, deployment"},
        {"id": "09", "title": "Docker Containerization", "emoji": "🐳", "topics": "Multi-stage builds, optimization"},
        {"id": "10", "title": "Testing Best Practices", "emoji": "✅", "topics": "Unit, integration, E2E tests"},
        {"id": "11", "title": "CI/CD with GitHub Actions", "emoji": "🔄", "topics": "Workflows, automation, deployment"},
    ]
}

# Example questions by category
EXAMPLE_QUESTIONS = {
    "Getting Started": [
        "What is artificial intelligence and how does it work?",
        "How do I start learning machine learning?",
        "What's the difference between AI, ML, and deep learning?",
    ],
    "RAG & LangChain": [
        "What is Retrieval Augmented Generation?",
        "How does RAG improve LLM responses?",
        "Explain vector databases in simple terms",
        "What is LangChain used for?",
    ],
    "Technical": [
        "How do embeddings work?",
        "What's the difference between FAISS and Pinecone?",
        "How do I implement a RAG system?",
        "What are best practices for prompt engineering?",
    ],
    "Development": [
        "How do I deploy an AI model as an API?",
        "What are best practices for testing AI applications?",
        "How do I dockerize my ML application?",
        "How do I set up CI/CD for AI projects?",
    ]
}

# Page configuration
st.set_page_config(
    page_title="Learn AI with RAG",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .answer-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-top: 1rem;
    }
    .lesson-card {
        background-color: #f8f9fa;
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
        border-left: 3px solid #1f77b4;
    }
    .progress-stat {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'lessons_visited' not in st.session_state:
    st.session_state.lessons_visited = set()
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0

# Sidebar
with st.sidebar:
    st.markdown("## 🎓 About This Tutor")
    st.markdown("""
    An **interactive AI Engineering tutor** powered by Retrieval Augmented Generation (RAG).

    **Learn by asking questions!** The tutor searches through 17 comprehensive lessons
    and provides clear, educational answers in your language (English or Italian).
    """)

    # Progress tracking
    st.markdown("### 📊 Your Progress")
    total_lessons = sum(len(lessons) for lessons in LESSONS.values())
    lessons_visited = len(st.session_state.lessons_visited)
    progress = lessons_visited / total_lessons if total_lessons > 0 else 0

    st.markdown(f"""
    <div class="progress-stat">
        <h3>{st.session_state.total_questions}</h3>
        <p style="margin:0;">Questions Asked</p>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress)
    st.caption(f"Explored {lessons_visited} of {total_lessons} lesson topics")

    st.markdown("---")

    # Lesson Catalog
    st.markdown("### 📚 Lesson Catalog")

    selected_level = st.selectbox(
        "Choose Level:",
        ["Beginner", "Intermediate", "Advanced"],
        key="level_selector"
    )

    for lesson in LESSONS[selected_level]:
        with st.expander(f"{lesson['emoji']} Lesson {lesson['id']}: {lesson['title']}"):
            st.caption(lesson['topics'])
            if st.button(f"Ask about this →", key=f"lesson_{lesson['id']}"):
                st.session_state.current_question = f"Tell me about {lesson['title'].lower()}"
                st.session_state.lessons_visited.add(lesson['id'])

    st.markdown("---")

    # Language preference
    st.markdown("### 🌍 Language")
    language = st.radio(
        "Preferred response language:",
        ["Auto-detect", "English", "Italian"],
        help="The tutor will respond in your chosen language"
    )

    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.info("""
    - Be specific in your questions
    - Ask follow-up questions to dive deeper
    - Try example questions to get started
    - The tutor responds in your question's language!
    """)

# Main content
st.markdown('<div class="main-header">🤖 Learn AI with RAG</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your Interactive AI Engineering Tutor</div>', unsafe_allow_html=True)

# What is RAG explanation
with st.expander("ℹ️ How does this work? (Click to learn)", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🔍 What is RAG?

        **RAG** = **Retrieval Augmented Generation**

        1. **📚 Retrieval**: When you ask a question, the system searches
           through 17 comprehensive lessons to find relevant information

        2. **🤖 Generation**: An AI tutor (GPT-4) reads that information
           and generates a clear, personalized answer just for you

        It's like having a smart teacher who has studied all the lessons
        and can explain anything conversationally!
        """)

    with col2:
        st.markdown("""
        ### ✨ Why RAG for Learning?

        - ✅ **Interactive**: Ask questions in your own words
        - ✅ **Comprehensive**: Answers based on detailed lesson content
        - ✅ **Multilingual**: Ask in English or Italian
        - ✅ **Adaptive**: Explanations tailored to your question
        - ✅ **24/7 Available**: Learn at your own pace, anytime
        - ✅ **No Hallucinations**: Answers grounded in actual lessons
        """)

# Check API health
def check_api_health() -> bool:
    """Check if backend API is accessible"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# API status indicator
api_healthy = check_api_health()

if not api_healthy:
    st.error(f"""
    ⚠️ **Cannot connect to the tutor API** at `{API_URL}`

    **To fix this:**
    1. Make sure the backend is running: `cd backend && uvicorn main:app --reload`
    2. Check that the backend is running on port 8000
    3. Or use docker-compose: `docker-compose up`
    """)
    st.stop()
else:
    st.success("✅ Tutor is online and ready to help!")

# Example questions section
st.markdown("### 💡 Not sure what to ask? Try these examples:")

tabs = st.tabs(list(EXAMPLE_QUESTIONS.keys()))

for tab, (category, questions) in zip(tabs, EXAMPLE_QUESTIONS.items()):
    with tab:
        cols = st.columns(2)
        for idx, question in enumerate(questions):
            col = cols[idx % 2]
            with col:
                if st.button(f"💭 {question}", key=f"ex_{category}_{idx}"):
                    st.session_state.current_question = question

st.markdown("---")

# Main query interface
st.markdown("### 💬 Ask Your Question")

# Get question from session state or user input
question = st.text_area(
    "What would you like to learn about AI Engineering?",
    value=st.session_state.get('current_question', ''),
    placeholder="e.g., What is a vector database and why is it useful for AI applications?",
    help="Ask anything about AI, ML, LangChain, RAG, or related topics. I'll respond in your question's language!",
    height=100
)

# Clear the session state after using it
if 'current_question' in st.session_state:
    del st.session_state.current_question

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    ask_button = st.button("🚀 Ask Tutor", type="primary", use_container_width=True)

with col2:
    if st.button("🔄 Clear", use_container_width=True):
        question = ""
        st.rerun()

with col3:
    show_history = st.checkbox("Show History", value=False)

if ask_button and question:
    with st.spinner("🤔 Searching through lessons and generating answer..."):
        try:
            # Add language instruction if specific language chosen
            enhanced_question = question
            if language == "Italian":
                enhanced_question = f"[Rispondi in italiano] {question}"
            elif language == "English":
                enhanced_question = f"[Respond in English] {question}"

            # Call the API
            response = requests.post(
                f"{API_URL}/query",
                json={"question": enhanced_question},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer received")

                # Update stats
                st.session_state.total_questions += 1

                # Display the answer
                st.markdown("### 📖 Answer:")
                st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

                # Add to history
                st.session_state.history.append({
                    "question": question,
                    "answer": answer
                })

                # Suggest related topics
                st.markdown("---")
                st.markdown("### 🔗 Want to learn more?")
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("🧠 Related: Neural Networks"):
                        st.session_state.current_question = "How do neural networks work?"
                        st.rerun()

                with col2:
                    if st.button("🔍 Related: Vector Databases"):
                        st.session_state.current_question = "What are vector databases?"
                        st.rerun()

                with col3:
                    if st.button("⛓️ Related: LangChain"):
                        st.session_state.current_question = "What is LangChain used for?"
                        st.rerun()

            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The question might be complex. Try rephrasing or breaking it into smaller questions!")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

elif ask_button and not question:
    st.warning("⚠️ Please enter a question first!")

# Show conversation history
if show_history and st.session_state.history:
    st.markdown("---")
    st.markdown("### 📜 Your Learning Journey")

    # Show most recent first
    for i, item in enumerate(reversed(st.session_state.history[-10:])):  # Last 10
        with st.expander(f"Q{len(st.session_state.history) - i}: {item['question'][:80]}...", expanded=False):
            st.markdown(f"**Question:** {item['question']}")
            st.markdown(f"**Answer:** {item['answer']}")

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔁 Ask Again", key=f"reask_{i}"):
                    st.session_state.current_question = item['question']
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0; background-color: #f8f9fa; border-radius: 0.5rem;">
    <h4>🎓 Learn AI with RAG</h4>
    <p>Built with ❤️ using <strong>FastAPI</strong>, <strong>LangChain</strong>, <strong>FAISS</strong>, and <strong>Streamlit</strong></p>
    <p><strong>17 Comprehensive Lessons</strong> | <strong>Multilingual Support</strong> (EN/IT) | <strong>Production-Ready Stack</strong></p>
    <p style="margin-top: 1rem;">
        <a href="https://github.com/euxhenjonex/learn-ai-with-rag" target="_blank" style="color: #1f77b4; text-decoration: none;">
            ⭐ View on GitHub
        </a>
    </p>
</div>
""", unsafe_allow_html=True)
