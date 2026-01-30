# intake/intake_agent.py
"""
Intake agent for SAFE-INTERN.

Responsibilities:
- Convert raw cleaned text into structured IntakeSchema
- Uses OpenRouter LLM (JSON-only)
- Safe fallback if LLM fails

ONLY FILE USING OPENROUTER
"""

from typing import Dict, Any
import os
import re
import json
import requests

from intake.schema import IntakeSchema, build_intake_schema
from config.settings import (
    LLM_ENABLED,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


# ---------- FALLBACK (SAFE MODE) ----------

def fallback_structuring(text: str) -> Dict[str, Any]:
    email_match = re.search(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text
    )
    url_match = re.search(r"https?://\S+|www\.\S+", text)

    payment_keywords = ["fee", "payment", "deposit", "registration", "charges"]
    urgency_keywords = ["urgent", "immediately", "limited", "asap", "hurry"]

    return {
        "clean_text": text,

        "company_name": None,
        "contact_person": None,
        "email": email_match.group(0) if email_match else None,
        "phone": None,
        "website": url_match.group(0) if url_match else None,
        "social_media": [],

        "job_title": None,
        "job_description": None,
        "location": None,
        "duration": None,
        "compensation": None,
        "start_date": None,

        "payment_mentions": any(k in text.lower() for k in payment_keywords),
        "payment_required": False,
        "payment_amount": None,

        "urgency_mentions": any(k in text.lower() for k in urgency_keywords),
        "urgency_phrases": [],

        "interview_process_described": False,
        "communication_channels": [],

        "missing_information": [],
        "unusual_patterns": {},
        "entities": {},

        "input_length": len(text),
        "language_detected": None,
    }


# ---------- OPENROUTER LLM ----------

def run_llm_intake(text: str) -> Dict[str, Any]:
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    system_prompt = """
You are an intake parser for an internship safety system.

Rules:
- Output ONLY valid JSON
- Do NOT add explanations
- Do NOT accuse or judge
- Use null when information is missing

Return JSON matching this structure:

{
  "clean_text": string,
  "company_name": string | null,
  "email": string | null,
  "website": string | null,
  "payment_mentions": boolean,
  "payment_required": boolean,
  "urgency_mentions": boolean,
  "input_length": number
}
"""

    payload = {
        "model": LLM_MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=15
    )

    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    return json.loads(content)


# ---------- MAIN ENTRY ----------

def run_intake(text: str) -> IntakeSchema:
    if not text or not text.strip():
        raise ValueError("Input text is empty")

    if not LLM_ENABLED:
        structured = fallback_structuring(text)
    else:
        try:
            structured = run_llm_intake(text)
        except Exception:
            structured = fallback_structuring(text)

    return build_intake_schema(structured)
