# 🧠 AI Text Summarizer & Rewriter API

A FastAPI-based microservice that integrates **OpenAI GPT models** to summarize and rewrite text dynamically.

This project is part of the [AI Prototypes Collection](https://github.com/euxhenjonex/ai-prototypes) by **Euxhenjo Nexhipi**, showcasing practical AI integrations for real-world use.

---

## 🚀 Features

✅ **/summarize** – Generate clear, concise summaries of any text.  
✅ **/rewrite** – Rewrite text in a selected tone (e.g., professional, creative, simple).  
✅ Built with **FastAPI + OpenAI API** for rapid prototyping.  
✅ Environment variable management via `.env`.  

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **FastAPI**
- **Uvicorn**
- **OpenAI API**
- **python-dotenv**

---

## 📦 Installation

1️⃣ **Clone the repository**
```bash
git clone https://github.com/euxhenjonex/ai-prototypes.git
cd ai-prototypes/01-text-api
```

2️⃣ **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

4️⃣ **Set your OpenAI API key**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

---

## 🧠 Usage
▶️ **Run the API**
```bash
uvicorn main:app --reload
```

🌐 **Open the interactive docs**  
Go to: http://127.0.0.1:8000/docs

---

## 🧩 API Endpoints

### `GET /`
Check API status.

**Response:**
```json
{"message": "AI Summarizer API is running 🚀"}
```

### `POST /summarize`
Summarizes input text.

**Example Request:**
```json
{
  "text": "Artificial Intelligence is transforming how people work and communicate."
}
```

**Example Response:**
```json
{
  "summary": "AI is transforming work and communication through automation and innovation."
}
```

### `POST /rewrite`
Rewrites text in a chosen tone.

**Example Request:**
```json
{
  "text": "Artificial Intelligence is changing how people work and communicate.",
  "tone": "creative"
}
```

**Example Response:**
```json
{
  "original_text": "Artificial Intelligence is changing how people work and communicate.",
  "tone": "creative",
  "rewritten_text": "Artificial Intelligence is revolutionizing the way we connect and collaborate, weaving a new tapestry of innovation and creativity."
}
```

---

## ✨ Author

Euxhenjo Nexhipi
💼 euxhenjonex.com

🚀 AI Solution Specialist & Automation Builder