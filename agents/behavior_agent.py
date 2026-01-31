# agents/behavior_agent.py

HARD_URGENCY_WORDS = [
    "urgent", "immediately", "asap", "within 24 hours", "24 hours",
    "deadline", "last date", "final day", "hours left", "apply now",
    "pay now", "today only"
]

SCARCITY_WORDS = [
    "limited slots", "only", "few seats", "mentor bandwidth",
    "we will onboard only", "limited intake"
]

MANIPULATION_PHRASES = [
    "guaranteed placement", "no interview required",
    "100% placement", "instant selection",
    "whatsapp confirmation", "confirm your seat",
    "seat confirmation", "selected for internship",
    "confirm seat now", "instant confirmation"
]

PROCESS_KEYWORDS = [
    "interview", "assessment", "screening", "selection",
    "resume screening", "technical interview", "hr discussion",
    "online interaction", "call with founders"
]

def run_behavior_agent(intake_data: dict) -> dict:
    text = (intake_data.get("raw_text") or intake_data.get("clean_text") or "").lower()
    observations = []

    hard_urgency_hits = [w for w in HARD_URGENCY_WORDS if w in text]
    scarcity_hits = [w for w in SCARCITY_WORDS if w in text]
    manipulation_hits = [w for w in MANIPULATION_PHRASES if w in text]

    if hard_urgency_hits:
        observations.append("Strong urgency / pressure language detected")

    if scarcity_hits:
        observations.append("Scarcity language detected (limited slots)")

    if manipulation_hits:
        observations.append("Manipulative or guaranteed outcome language detected")

    if not any(k in text for k in PROCESS_KEYWORDS):
        observations.append("No clear interview or selection process mentioned")

    if not observations:
        observations.append("No concerning behavioral patterns detected")

    return {
        "hard_urgency_terms": hard_urgency_hits,
        "scarcity_terms": scarcity_hits,
        "manipulation_terms": manipulation_hits,
        "observations": observations
    }