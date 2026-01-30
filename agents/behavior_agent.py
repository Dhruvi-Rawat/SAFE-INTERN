# agents/behavior_agent.py
"""
Behavior agent for SAFE-INTERN (Rule-based).

Detects:
- Urgency language
- Manipulation phrases
- Missing interview process

NO LLM
NO CrewAI
"""

URGENCY_WORDS = [
    "urgent", "immediately", "asap", "limited time",
    "apply now", "hurry", "deadline"
]

MANIPULATION_PHRASES = [
    "guaranteed placement", "no interview required",
    "100% placement", "instant selection"
]

PROCESS_KEYWORDS = [
    "interview", "assessment", "screening", "selection"
]


def run_behavior_agent(intake_data: dict) -> dict:
    text = intake_data.get("clean_text", "").lower()
    observations = []

    urgency_hits = [w for w in URGENCY_WORDS if w in text]
    manipulation_hits = [w for w in MANIPULATION_PHRASES if w in text]

    if urgency_hits:
        observations.append("Urgency-focused language detected")

    if manipulation_hits:
        observations.append("Manipulative or guaranteed outcome language detected")

    if not any(k in text for k in PROCESS_KEYWORDS):
        observations.append("No clear interview or selection process mentioned")

    if not observations:
        observations.append("No concerning behavioral patterns detected")

    return {
        "urgency_terms": urgency_hits,
        "manipulation_terms": manipulation_hits,
        "observations": observations
    }
