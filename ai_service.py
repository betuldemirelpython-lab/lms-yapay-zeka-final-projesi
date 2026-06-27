# ai_service.py
"""FastAPI backend that provides AI-powered endpoints for the LMS.
Uses OpenAI, Gemini, or Groq based on available API keys in .env.
Falls back to a mock response if no API key is configured.
"""

import os
from typing import Any, Dict, List

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
MODEL_NAME     = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

# Detect which provider to use
def _detect_provider() -> str:
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your-"):
        return "openai"
    if GEMINI_API_KEY and not GEMINI_API_KEY.startswith("your-"):
        return "gemini"
    if GROQ_API_KEY and not GROQ_API_KEY.startswith("your-"):
        return "groq"
    return "mock"

PROVIDER = _detect_provider()

app = FastAPI(title="LMS AI Service", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from database import init_db
    init_db()

# ----- Pydantic models -----
class AnalyzeRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    analysis: str
    provider: str

class SummarizeRequest(BaseModel):
    content: str

class SummarizeResponse(BaseModel):
    summary: str
    provider: str

# ----- LLM helpers -----

async def call_openai(messages: List[Dict[str, str]]) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": MODEL_NAME, "messages": messages, "temperature": 0.7}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers, json=payload, timeout=30
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"OpenAI hatası: {resp.text}")
        return resp.json()["choices"][0]["message"]["content"].strip()


async def call_gemini(messages: List[Dict[str, str]]) -> str:
    """Call Google Gemini via REST API."""
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_msg   = next((m["content"] for m in messages if m["role"] == "user"),   "")
    prompt = f"{system_msg}\n\n{user_msg}" if system_msg else user_msg

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-pro:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, timeout=30)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Gemini hatası: {resp.text}")
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


async def call_groq(messages: List[Dict[str, str]]) -> str:
    """Call Groq (OpenAI-compatible) API."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    groq_model = "llama-3.3-70b-versatile"
    payload = {"model": groq_model, "messages": messages, "temperature": 0.7}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=30
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Groq hatası: {resp.text}")
        return resp.json()["choices"][0]["message"]["content"].strip()


async def call_mock(messages: List[Dict[str, str]]) -> str:
    """Mock LLM response – no API key required (demo/test mode)."""
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
    words = len(user_msg.split())
    return (
        f"[DEMO MOD – Gerçek API anahtarı girilmedi]\n\n"
        f"Metin analizi tamamlandı. Girilen metin {words} kelimeden oluşmaktadır. "
        "Gerçek AI analizi için lütfen .env dosyasına geçerli bir OPENAI_API_KEY, "
        "GEMINI_API_KEY veya GROQ_API_KEY girin."
    )


async def call_llm(messages: List[Dict[str, str]]) -> str:
    if PROVIDER == "openai":
        return await call_openai(messages)
    elif PROVIDER == "gemini":
        return await call_gemini(messages)
    elif PROVIDER == "groq":
        return await call_groq(messages)
    else:
        return await call_mock(messages)

# ----- Endpoints -----

@app.get("/health")
async def health_check():
    return {"status": "ok", "provider": PROVIDER}


@app.post("/analyze_text", response_model=AnalyzeResponse)
async def analyze_text(req: AnalyzeRequest):
    """Öğrenci metnini AI ile analiz eder."""
    system_prompt = (
        "Sen bir eğitim asistanısın. Verilen öğrenci metnini analiz et; "
        "yapıcı geri bildirim, anahtar kavramlar ve geliştirme önerileri sun. "
        "Yanıtını Türkçe ver."
    )
    try:
        result = await call_llm([
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": req.text},
        ])
        return AnalyzeResponse(analysis=result, provider=PROVIDER)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/summarize_content", response_model=SummarizeResponse)
async def summarize_content(req: SummarizeRequest):
    """Verilen içeriği 2-3 cümleyle özetler."""
    system_prompt = (
        "Sen özlü bir özetleyicisin. Verilen metni 2-3 cümleyle özetle; "
        "ana fikirleri koru. Türkçe yanıt ver."
    )
    try:
        result = await call_llm([
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": req.content},
        ])
        return SummarizeResponse(summary=result, provider=PROVIDER)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("ai_service:app", host="0.0.0.0", port=8000, reload=True)
