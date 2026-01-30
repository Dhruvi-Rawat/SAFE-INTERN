# utils/risk_engine.py
"""
Risk engine for SAFE-INTERN.

Responsibilities:
- Combine signals from all agents
- Produce a final advisory risk score (0–100)
- Assign a risk category (Low / Caution / High Indicators)
- Provide transparent breakdown

NO accusations
NO absolute claims
NO data storage
"""

from typing import Dict, Any, Tuple, List


# ---------- CONFIGURATION ----------

AGENT_MAX_SCORES = {
    "company": 30,
    "payment": 30,
    "behavior": 20,
    "ml": 20
}

RISK_CATEGORIES = [
    (30, "Low Risk Indicators"),
    (60, "Caution Advised"),
    (100, "High Risk Indicators")
]

# These rules MUST match actual agent observations
COMPANY_RULES = {
    "not reachable": 10,
    "does not use https": 5,
    "free email domain": 10,
    "does not match website domain": 5
}

PAYMENT_RULES = {
    "payment appears to be requested before": 15,
    "specific payment amount": 10,
    "high-pressure language": 5
}

BEHAVIOR_RULES = {
    "urgency_terms": 10,
    "manipulation_terms": 10
}

ML_SCORES = {
    "low": 5,
    "medium": 12,
    "high": 20
}


# ---------- SCORING FUNCTIONS ----------

def score_company(result: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 0
    reasons = []

    for obs in result.get("observations", []):
        obs_lower = obs.lower()
        for rule, points in COMPANY_RULES.items():
            if rule in obs_lower:
                score += points
                reasons.append(f"{rule} (+{points})")

    return min(score, AGENT_MAX_SCORES["company"]), reasons


def score_payment(result: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 0
    reasons = []

    for obs in result.get("observations", []):
        obs_lower = obs.lower()
        for rule, points in PAYMENT_RULES.items():
            if rule in obs_lower:
                score += points
                reasons.append(f"{rule} (+{points})")

    return min(score, AGENT_MAX_SCORES["payment"]), reasons


def score_behavior(result: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 0
    reasons = []

    if result.get("urgency_terms"):
        score += BEHAVIOR_RULES["urgency_terms"]
        reasons.append("urgency language detected")

    if result.get("manipulation_terms"):
        score += BEHAVIOR_RULES["manipulation_terms"]
        reasons.append("manipulation phrases detected")

    return min(score, AGENT_MAX_SCORES["behavior"]), reasons


def score_ml(ml_result: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Score ML signal using probability and confidence.

    ML is advisory and capped.
    """
    if not ml_result or not ml_result.get("ml_used"):
        return 0, ["ML analysis not performed"]

    risk_level = ml_result.get("risk_level", "low")
    probability = ml_result.get("risk_probability", 0.0)

    # Base score by level
    base_scores = {
        "low": 5,
        "medium": 12,
        "high": 20
    }

    base = base_scores.get(risk_level, 0)

    # Confidence = distance from 0.5
    confidence = abs(probability - 0.5) * 2  # range 0–1

    # Final ML score
    score = int(round(base * confidence))
    score = min(score, AGENT_MAX_SCORES["ml"])

    explanation = [
        f"ML language analysis indicates {risk_level} risk "
        f"(probability: {probability}, confidence: {round(confidence, 2)}) (+{score})"
    ]

    return score, explanation


# ---------- CATEGORY ----------

def get_risk_category(score: int) -> str:
    for threshold, label in RISK_CATEGORIES:
        if score < threshold:
            return label
    return RISK_CATEGORIES[-1][1]


# ---------- MAIN ENGINE ----------

def calculate_risk(agent_results: Dict[str, Any]) -> Dict[str, Any]:
    breakdown = {}
    details = {}
    total = 0

    if agent_results.get("company"):
        s, d = score_company(agent_results["company"])
        breakdown["company"] = s
        details["company"] = d
        total += s
    else:
        breakdown["company"] = 0
        details["company"] = ["not analyzed"]

    if agent_results.get("payment"):
        s, d = score_payment(agent_results["payment"])
        breakdown["payment"] = s
        details["payment"] = d
        total += s
    else:
        breakdown["payment"] = 0
        details["payment"] = ["not analyzed"]

    if agent_results.get("behavior"):
        s, d = score_behavior(agent_results["behavior"])
        breakdown["behavior"] = s
        details["behavior"] = d
        total += s
    else:
        breakdown["behavior"] = 0
        details["behavior"] = ["not analyzed"]

    if agent_results.get("ml"):
        s, d = score_ml(agent_results["ml"])
        breakdown["ml"] = s
        details["ml"] = d
        total += s
    else:
        breakdown["ml"] = 0
        details["ml"] = ["not analyzed"]

    total = min(total, 100)

    return {
        "risk_score": total,
        "risk_category": get_risk_category(total),
        "breakdown": breakdown,
        "details": details
    }
