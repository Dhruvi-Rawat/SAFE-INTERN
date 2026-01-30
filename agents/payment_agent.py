# agents/payment_agent.py
"""
Payment agent for SAFE-INTERN using CrewAI.

Responsibilities:
- Detect mentions of payment or fees
- Identify upfront payment requests
- Extract mentioned payment amounts (if any)
- Report observations in neutral, advisory language

NO risk scoring
NO accusations
NO assumptions
"""

from typing import Dict, Any, List
import re

from crewai import Agent
from crewai.tasks import Task


# ---------- KEYWORDS ----------

PAYMENT_KEYWORDS = [
    "fee",
    "fees",
    "payment",
    "pay",
    "deposit",
    "registration",
    "training fee",
    "processing fee",
    "joining fee",
    "course fee"
]

UPFRONT_KEYWORDS = [
    "before joining",
    "prior to joining",
    "advance payment",
    "pay first",
    "initial payment",
    "upfront",
    "pay now",
    "required to pay"
]


# ---------- CREWAI AGENT ----------

agent = Agent(
    role="Payment Pattern Analyst",
    goal="Identify payment-related patterns in internship communications",
    backstory=(
        "You analyze internship-related messages to identify mentions of "
        "fees or payments. You report factual observations without making "
        "judgments or accusations."
    ),
    allow_delegation=False,
    verbose=False
)


# ---------- HELPER FUNCTIONS ----------

def detect_payment_mentions(text: str) -> bool:
    """Check if any payment-related keyword is present"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in PAYMENT_KEYWORDS)


def detect_upfront_payment(text: str) -> bool:
    """Check if payment is requested before joining"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in UPFRONT_KEYWORDS)


def extract_payment_amount(text: str) -> str | None:
    """
    Extract payment amount if mentioned.
    Examples: ₹5000, Rs. 3000, 1000 INR
    """
    patterns = [
        r"₹\s?\d+",
        r"rs\.?\s?\d+",
        r"\d+\s?inr"
    ]

    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group().upper()

    return None


# ---------- MAIN ANALYSIS ----------

def analyze_payment(intake_data: Dict[str, Any]) -> Dict[str, Any]:
    observations: List[str] = []

    text = intake_data.get("clean_text", "")

    payment_mentioned = detect_payment_mentions(text)
    upfront_payment = detect_upfront_payment(text)
    payment_amount = extract_payment_amount(text)

    if payment_mentioned:
        observations.append("The communication mentions payment or fees.")
    else:
        observations.append("No payment or fee-related language was detected.")

    if upfront_payment:
        observations.append(
            "Payment appears to be requested before internship commencement."
        )

    if payment_amount:
        observations.append(
            f"A specific payment amount was mentioned ({payment_amount})."
        )

    return {
        "payment_mentioned": payment_mentioned,
        "upfront_payment": upfront_payment,
        "payment_amount": payment_amount,
        "observations": observations
    }


# ---------- TASK CREATION ----------

def create_task(intake_data: Dict[str, Any]) -> Task:
    analysis = analyze_payment(intake_data)

    description = f"""
Analyze the following internship communication for payment-related patterns.

Observations:
{chr(10).join(f"- {o}" for o in analysis['observations'])}

Rules:
- Be factual and neutral
- Do NOT accuse or confirm fraud
- Do NOT assign any score
"""

    return Task(
        description=description,
        agent=agent,
        expected_output=(
            "A neutral summary describing whether payment or fee-related "
            "language was present and whether upfront payment was requested."
        )
    )
