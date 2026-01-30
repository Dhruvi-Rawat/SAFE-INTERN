# intake/intake_agent.py
"""
Intake agent for SAFE-INTERN.

Responsibilities:
- Structure cleaned text into IntakeSchema
- Use deterministic fallback by default
- Optionally delegate to LLM intake
- NO scoring
- NO judgments
"""

from typing import Dict, Any
import re

from config.settings import LLM_ENABLED
from intake.schema import build_intake_schema, IntakeSchema

import os
import json
import requests

from config.settings import (
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS
)
from config.prompts import INTAKE_SYSTEM_PROMPT

# ------------------------------------------------------------------
# FALLBACK STRUCTURING (DETERMINISTIC)
# ------------------------------------------------------------------

def fallback_structuring(text: str) -> Dict[str, Any]:
    text_lower = text.lower()

    email_match = re.search(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text
    )
    url_match = re.search(r"https?://\S+|www\.\S+", text)

    payment_keywords = ["fee", "payment", "deposit", "registration", "charges"]
    urgency_keywords = ["urgent", "immediately", "limited", "asap", "hurry"]

    payment_mentions = any(k in text_lower for k in payment_keywords)
    urgency_mentions = any(k in text_lower for k in urgency_keywords)

    missing_information = []
    if not url_match:
        missing_information.append("website")
    if not email_match:
        missing_information.append("email")
    missing_information.extend(["company_name", "job_title", "interview_process"])

    return {
        # Core
        "clean_text": text,

        # Basic details
        "company_name": None,
        "contact_person": None,
        "email": email_match.group(0) if email_match else None,
        "phone": None,
        "website": url_match.group(0) if url_match else None,
        "social_media": [],

        # Job info
        "job_title": None,
        "job_description": None,
        "location": None,
        "duration": None,
        "compensation": None,
        "start_date": None,

        # Pattern indicators
        "payment_mentions": payment_mentions,
        "payment_required": False,
        "payment_amount": None,

        "urgency_mentions": urgency_mentions,
        "urgency_phrases": [],

        "interview_process_described": False,
        "communication_channels": [],

        # Missing info
        "missing_information": missing_information,

        # Unusual patterns (schema-complete)
        "unusual_patterns": {
            "requests_personal_financial_info": False,
            "requests_upfront_payment": False,
            "uses_free_email_domain": False,
            "communication_via_messaging_app": False,
            "promises_guaranteed_placement": False,
            "mentions_easy_money": False,
            "requires_immediate_decision": urgency_mentions,
            "lacks_company_details": True,
            "grammar_or_formatting_issues": False,
            "requests_credential_sharing": False
        },

        # Entities (schema-complete)
        "entities": {
            "companies_mentioned": [],
            "people_mentioned": [],
            "locations_mentioned": [],
            "technologies_mentioned": []
        },

        # Metadata
        "input_length": len(text),
        "language_detected": None
    }


# ------------------------------------------------------------------
# MAIN ENTRY
# ------------------------------------------------------------------

def run_intake(text: str) -> IntakeSchema:
    if not text or not text.strip():
        raise ValueError("Input text is empty")

    if LLM_ENABLED:
        structured_data = run_llm_intake(text)
    else:
        structured_data = fallback_structuring(text)

    return build_intake_schema(structured_data)


# ------------------------------------------------------------------
# LLM PLACEHOLDER
# ------------------------------------------------------------------

def run_llm_intake(text: str) -> Dict[str, Any]:
    api_key = os.getenv("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")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    payload = {
        "model": LLM_MODEL_NAME,
        "messages": [
            {"role": "system", "content": INTAKE_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15
    )

    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    return json.loads(content)
