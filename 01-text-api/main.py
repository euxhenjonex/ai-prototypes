from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from pathlib import Path
from openai import OpenAI

# Carica .env dal percorso corrente
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Inizializza client OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file.")

client = OpenAI(api_key=api_key)

# Inizializza FastAPI
app = FastAPI(title="AI Text Summarizer & Rewriter API")

# Modelli di input
class TextInput(BaseModel):
    text: str

class RewriteInput(BaseModel):
    text: str
    tone: str = "professional"  # default

# --- ENDPOINTS ---

@app.get("/")
async def root():
    return {"message": "AI Summarizer API is running 🚀"}

@app.post("/summarize")
async def summarize_text(input_data: TextInput):
    """Riassume il testo fornito."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes text clearly and concisely."},
                {"role": "user", "content": f"Summarize this text:\n{input_data.text}"}
            ],
            temperature=0.5
        )
        return {"summary": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rewrite")
async def rewrite_text(input_data: RewriteInput):
    """Riscrive il testo con un tono specifico."""
    try:
        prompt = f"Rewrite the following text in a {input_data.tone} tone:\n{input_data.text}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites text according to tone."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return {
            "original_text": input_data.text,
            "tone": input_data.tone,
            "rewritten_text": response.choices[0].message.content.strip()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
