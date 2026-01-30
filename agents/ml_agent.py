# agents/ml_agent.py
"""
ML agent for SAFE-INTERN.

Responsibilities:
- Load TF-IDF vectorizer and Logistic Regression model
- Perform language-based risk inference
- Store ML patterns for system learning
- Return advisory ML signal (not final decision)

NO training
NO final verdict
NO accusations
"""

from typing import Dict, Any, Tuple
import os
import pickle
import logging

from crewai import Agent
from crewai.tasks import Task

from database.metadata_repository import upsert_metadata
from database.pattern_repository import record_pattern

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- MODEL PATHS ----------
MODEL_DIR = "ml"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

MIN_TEXT_LENGTH = 20

# ---------- MODEL CACHE ----------
_MODEL_CACHE = None
_METADATA_REGISTERED = False


# ---------- METADATA ----------
def register_ml_metadata(model, vectorizer) -> None:
    """Store ML model metadata in DB (runs once)."""
    upsert_metadata("ml_model_name", type(model).__name__, "ML classifier")
    upsert_metadata("ml_vectorizer", type(vectorizer).__name__, "Vectorizer used")
    upsert_metadata("ml_pipeline", "TF-IDF + Logistic Regression", "ML pipeline")
    upsert_metadata(
        "ml_feature_count",
        str(len(vectorizer.get_feature_names_out())),
        "Number of TF-IDF features"
    )


# ---------- LOAD MODEL ----------
def load_model() -> Tuple[Any, Any]:
    global _MODEL_CACHE, _METADATA_REGISTERED

    if _MODEL_CACHE:
        return _MODEL_CACHE

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("ML model file missing")

    if not os.path.exists(VECTORIZER_PATH):
        raise FileNotFoundError("ML vectorizer file missing")

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)

    if not _METADATA_REGISTERED:
        try:
            register_ml_metadata(model, vectorizer)
            _METADATA_REGISTERED = True
        except Exception as e:
            logger.warning(f"Metadata registration skipped: {e}")

    _MODEL_CACHE = (model, vectorizer)
    return model, vectorizer


# ---------- CREWAI AGENT ----------
agent = Agent(
    role="Language Pattern Analyst",
    goal="Detect risky language patterns using ML",
    backstory="You provide advisory insights only, never final decisions.",
    allow_delegation=False,
    verbose=False
)


# ---------- MAIN ANALYSIS ----------
def analyze_ml(intake_data: Dict[str, Any]) -> Dict[str, Any]:
    text = intake_data.get("clean_text", "")

    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return {"ml_used": False, "reason": "Insufficient text"}

    try:
        model, vectorizer = load_model()
        vector = vectorizer.transform([text])
        probability = float(model.predict_proba(vector)[0][1])

        if probability < 0.3:
            level = "low"
        elif probability < 0.6:
            level = "medium"
        else:
            level = "high"

        # ✅ STORE PATTERN
        record_pattern(
            source="ml",
            signal=level,
            confidence=round(probability, 3)
        )

        return {
            "ml_used": True,
            "risk_probability": round(probability, 3),
            "risk_level": level
        }

    except Exception as e:
        logger.error(f"ML inference failed: {e}")
        return {"ml_used": False, "reason": "ML unavailable"}


# ---------- TASK ----------
def create_task(intake_data: Dict[str, Any]) -> Task:
    analysis = analyze_ml(intake_data)

    description = f"""
Analyze the internship text using a trained ML model.

ML Result:
{analysis}

Rules:
- Advisory only
- No accusations
- No final decision
"""

    return Task(
        description=description,
        agent=agent,
        expected_output="Advisory ML risk signal"
    )
