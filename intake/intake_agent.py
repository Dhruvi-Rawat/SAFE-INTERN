# intake/intake_agent.py
"""
Intake agent for SAFE-INTERN.

- Structures cleaned text
- Uses fallback logic by default
- Enforces IntakeSchema
"""

from typing import Dict, Any
import re

from config.settings import LLM_ENABLED
from intake.schema import IntakeSchema, build_intake_schema


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
        "language_detected": None
    }


def run_intake(text: str) -> IntakeSchema:
    if not text or not text.strip():
        raise ValueError("Input text is empty")

    if not LLM_ENABLED:
        structured_data = fallback_structuring(text)
    else:
        structured_data = run_llm_intake(text)

    return build_intake_schema(structured_data)


def run_llm_intake(text: str) -> Dict[str, Any]:
    raise NotImplementedError(
        "LLM intake not enabled. Set LLM_ENABLED=True to activate."
    )
