# agents/behavior_agent.py
"""
Behavior agent for SAFE-INTERN using CrewAI.

Responsibilities:
- Detect urgency and pressure language
- Identify manipulation-related phrases
- Highlight absence of a clear selection process
- Report observations in neutral, advisory language

NO risk scoring | NO accusations | NO assumptions
"""

from typing import Dict, Any, List

from crewai import Agent,Task


# ---------- PATTERN DEFINITIONS ----------

URGENCY_KEYWORDS = [
    "urgent", "immediate", "asap", "limited time",
    "apply now", "last chance", "only today",
    "few slots left", "hurry", "deadline"
]

MANIPULATION_PHRASES = [
    "guaranteed placement", "no interview required",
    "easy money", "quick earnings", "100% placement",
    "instant selection", "direct joining",
    "no experience required"
]

PROCESS_KEYWORDS = [
    "interview", "selection", "screening",
    "assessment", "test", "hr round"
]


# ---------- CREWAI AGENT ----------

agent = Agent(
    role="Behavioral Pattern Analyst",
    goal="Identify urgency and manipulation patterns in internship communications",
    backstory=(
        "You analyze communication tone and structure to identify urgency, "
        "pressure, or manipulation patterns. You report observable signals "
        "without making accusations or judgments."
    ),
    allow_delegation=False,
    verbose=False
)


# ---------- PATTERN DETECTION ----------

def detect_urgency(text: str) -> List[str]:
    """Detect urgency-related phrases in text."""
    text_lower = text.lower()
    return [kw for kw in URGENCY_KEYWORDS if kw in text_lower]


def detect_manipulation(text: str) -> List[str]:
    """Detect manipulation-related phrases in text."""
    text_lower = text.lower()
    return [phrase for phrase in MANIPULATION_PHRASES if phrase in text_lower]


def detect_process_absence(text: str) -> bool:
    """Check whether a selection or interview process is mentioned."""
    text_lower = text.lower()
    return not any(keyword in text_lower for keyword in PROCESS_KEYWORDS)


# ---------- MAIN ANALYSIS ----------

def analyze_behavior(intake_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze behavioral patterns in internship communication.
    """
    text = intake_data.get("clean_text", "")

    urgency_hits = detect_urgency(text)
    manipulation_hits = detect_manipulation(text)
    process_absent = detect_process_absence(text)

    observations: List[str] = []

    if urgency_hits:
        observations.append(
            f"Urgency-related language detected ({', '.join(urgency_hits)})."
        )

    if manipulation_hits:
        observations.append(
            f"Manipulation-related phrases detected ({', '.join(manipulation_hits)})."
        )

    if process_absent:
        observations.append(
            "No clear interview or selection process was mentioned."
        )

    if not observations:
        observations.append(
            "No strong urgency or manipulation patterns were detected."
        )

    return {
        "urgency_terms": urgency_hits,
        "manipulation_terms": manipulation_hits,
        "process_absent": process_absent,
        "observations": observations
    }


# ---------- TASK CREATION ----------

def create_task(intake_data: Dict[str, Any]) -> Task:
    """Create CrewAI task for behavioral analysis."""
    analysis = analyze_behavior(intake_data)

    observations_text = "\n".join(
        f"- {obs}" for obs in analysis["observations"]
    )

    description = f"""
Analyze the following internship communication for behavioral patterns.

Observations:
{observations_text}

Rules:
- Be factual and neutral
- Do NOT accuse or confirm fraud
- Do NOT assign any score
"""

    return Task(
        description=description,
        agent=agent,
        expected_output=(
            "A neutral summary describing urgency, manipulation patterns, "
            "and whether a clear selection process was mentioned."
        )
    )
