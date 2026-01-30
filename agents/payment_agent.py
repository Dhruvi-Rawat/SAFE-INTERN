# agents/payment_agent.py
"""
Payment agent for SAFE-INTERN (Rule-based).

Detects:
- Payment mentions
- Upfront payment requests
- Amount mentions
- Pressure language

NO LLM
NO CrewAI
"""

import re

PAYMENT_KEYWORDS = [
    "fee", "payment", "deposit", "registration", "charges",
    "training fee", "joining fee", "processing fee"
]

UPFRONT_KEYWORDS = [
    "before joining", "pay first", "upfront",
    "immediate payment", "pay now"
]


def run_payment_agent(intake_data: dict) -> dict:
    text = intake_data.get("clean_text", "").lower()
    observations = []

    if any(k in text for k in PAYMENT_KEYWORDS):
        observations.append("Payment mentioned in the communication")

    if any(k in text for k in UPFRONT_KEYWORDS):
        observations.append("Payment appears to be requested before internship starts")

    amount_match = re.search(r"(₹|rs\.?|inr|\$)\s?\d+", text)
    if amount_match:
        observations.append("Specific payment amount mentioned")

    if not observations:
        observations.append("No unusual payment patterns detected")

    return {
        "observations": observations
    }
