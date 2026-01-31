# agents/payment_agent.py
"""
Payment agent for SAFE-INTERN (Rule-based).

Detects:
- Upfront payment
- Registration fees
- UPI / QR payment requests

Handles negation:
- "No fees involved" should NOT trigger risk
"""

import re

PAYMENT_KEYWORDS = [
    "registration fee",
    "processing fee",
    "training fee",
    "fee",
    "deposit",
    "upi",
    "paytm",
    "phonepe",
    "gpay",
    "google pay",
    "scan qr",
    "pay now",
    "confirm seat",
    "seat confirmation",
    "transfer money",
    "send payment",
]

UPFRONT_KEYWORDS = [
    "before joining",
    "pay first",
    "upfront",
    "immediate payment",
    "pay now",
]


def run_payment_agent(intake_data: dict) -> dict:
    text = (intake_data.get("raw_text") or intake_data.get("clean_text") or "").lower()
    observations = []

    # ✅ Negation patterns (trust signals)
    negation_phrases = [
        "no fee", "no fees", "no payment", "no payments",
        "no registration fee", "no application fee",
        "no charges", "free of cost", "without any fee"
    ]
    has_negation = any(p in text for p in negation_phrases)

    # keyword detection
    matches = [k for k in PAYMENT_KEYWORDS if k in text]

    if matches:
        # if negation exists, ignore generic words
        if has_negation:
            strong_only = [
                m for m in matches
                if m in ["upi", "paytm", "phonepe", "gpay", "google pay", "scan qr", "pay now", "send payment"]
            ]
            if strong_only:
                observations.append(f"Payment-related language detected: {', '.join(strong_only)}")
        else:
            observations.append(f"Payment-related language detected: {', '.join(matches)}")

    # upfront payment cues
    upfront_matches = [k for k in UPFRONT_KEYWORDS if k in text]
    if upfront_matches and not has_negation:
        observations.append("Payment appears to be requested before internship starts")

    # amount detection
    if not has_negation and re.search(r"(₹|rs\.?|inr|\$)\s*\d+", text):
        observations.append("Specific payment amount mentioned")

    # final fallback
    if not observations:
        if has_negation:
            observations.append("Explicitly states no fees/payment involved (trust signal)")
        else:
            observations.append("No unusual payment patterns detected")

    return {"observations": observations}