# agents/ml_agent.py
"""
ML agent for SAFE-INTERN.

Uses:
- TF-IDF vectorizer
- Logistic Regression model

NO training here
NO LLM
"""

import os
import pickle

MODEL_PATH = "ml/model.pkl"
VECTORIZER_PATH = "ml/vectorizer.pkl"
MIN_TEXT_LENGTH = 20


def run_ml_analysis(intake_data: dict) -> dict:
    text = intake_data.get("clean_text", "")

    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return {
            "ml_used": False,
            "reason": "Insufficient text for ML analysis"
        }

    if not (os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)):
        return {
            "ml_used": False,
            "reason": "ML model files not available"
        }

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)

    vector = vectorizer.transform([text])
    probability = model.predict_proba(vector)[0][1]

    if probability < 0.3:
        level = "low"
    elif probability < 0.6:
        level = "medium"
    else:
        level = "high"

    return {
        "ml_used": True,
        "risk_probability": round(float(probability), 3),
        "risk_level": level
    }
