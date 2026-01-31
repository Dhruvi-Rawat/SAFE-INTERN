from pathlib import Path
import re
import joblib

class MLAgent:
    def __init__(self, model_path="ml/model.pkl", vectorizer_path="ml/vectorizer.pkl"):
        self.model_path = Path(model_path)
        self.vectorizer_path = Path(vectorizer_path)

        if not self.model_path.exists() or not self.vectorizer_path.exists():
            raise FileNotFoundError(
                f"Missing ML files: {self.model_path} or {self.vectorizer_path}. "
                "Run ml/train_model.ipynb and save model.pkl + vectorizer.pkl."
            )

        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)

    def clean_text(self, t: str) -> str:
        t = str(t).lower().strip()
        t = re.sub(r"(https?://\S+|www\.\S+)", " URL ", t)
        t = re.sub(r"[^a-z0-9₹\s]", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def predict_prob(self, text: str) -> float:
        text = self.clean_text(text)
        vec = self.vectorizer.transform([text])

        # LogisticRegression -> predict_proba
        if hasattr(self.model, "predict_proba"):
            return float(self.model.predict_proba(vec)[0, 1])

        # LinearSVC -> decision_function + sigmoid
        import numpy as np
        score = float(self.model.decision_function(vec)[0])
        return float(1 / (1 + np.exp(-score)))

    def run(self, text: str) -> dict:
        p = self.predict_prob(text)          # 0–1
        risk = int(round(p * 100))           # 0–100

        return {
            "agent": "ml_agent",
            "risk_score": risk,
            "ml_probability": round(p, 4),
            "reason": "ML signal: similarity to known recruitment fraud language patterns."
        }