# utils/explanation_engine.py
"""
Explanation engine for SAFE-INTERN.

Responsibilities:
- Convert risk score and agent breakdown into user-friendly explanations
- Use advisory, non-accusatory language
- Explain why caution may be needed
- Provide practical next steps

NO accusations
NO legal conclusions
NO absolute claims
"""

from typing import Dict, Any, List


# ---------- DISCLAIMER ----------

DISCLAIMER = (
    "This assessment is advisory and based on observable patterns only. "
    "It does not confirm wrongdoing and should be used as guidance alongside "
    "independent verification."
)


# ---------- EXPLANATION BUILDERS ----------

def explain_company(details: List[str]) -> List[str]:
    explanations = []

    for d in details:
        d = d.lower()

        if "not reachable" in d:
            explanations.append(
                "The company website could not be reached, which may make verification difficult."
            )
        elif "does not use https" in d:
            explanations.append(
                "The company website does not use HTTPS, which is less common for established organizations."
            )
        elif "free email domain" in d:
            explanations.append(
                "Communication appears to use a free email domain rather than an official company domain."
            )
        elif "does not match website domain" in d:
            explanations.append(
                "The email domain does not match the website domain, which may require additional verification."
            )

    if not explanations:
        explanations.append(
            "No significant concerns were observed related to the company’s online presence."
        )

    return explanations


def explain_payment(details: List[str]) -> List[str]:
    explanations = []

    for d in details:
        d = d.lower()

        if "payment appears to be requested before" in d:
            explanations.append(
                "Payment is requested before the internship begins, which is uncommon and may require careful verification."
            )
        elif "specific payment amount" in d:
            explanations.append(
                "A specific payment amount is mentioned in the communication."
            )
        elif "high-pressure language" in d:
            explanations.append(
                "Time-sensitive language is used around payment, which may increase pressure on the applicant."
            )

    if not explanations:
        explanations.append(
            "No unusual payment-related patterns were detected."
        )

    return explanations


def explain_behavior(details: List[str]) -> List[str]:
    explanations = []

    for d in details:
        d = d.lower()

        if "urgency" in d:
            explanations.append(
                "Urgency-focused language is used, which may encourage rushed decision-making."
            )
        elif "manipulation" in d:
            explanations.append(
                "Certain phrases suggest guaranteed outcomes or simplified processes, which may warrant caution."
            )

    if not explanations:
        explanations.append(
            "The communication tone appears balanced without strong urgency or pressure."
        )

    return explanations


def explain_ml(details: List[str]) -> List[str]:
    explanations = []

    for d in details:
        d = d.lower()

        if "low" in d:
            explanations.append(
                "Language patterns are similar to lower-risk internship communications."
            )
        elif "medium" in d:
            explanations.append(
                "Some language patterns resemble those found in higher-risk communications."
            )
        elif "high" in d:
            explanations.append(
                "The language shows multiple patterns commonly associated with higher-risk internship messages."
            )

    if not explanations:
        explanations.append(
            "Machine learning analysis did not identify strong risk-related language patterns."
        )

    return explanations


# ---------- SUMMARY ----------

def generate_summary(risk_category: str, risk_score: int) -> str:
    if risk_category == "Low Risk Indicators":
        return (
            f"This internship communication shows relatively few concerning patterns "
            f"(risk score: {risk_score}/100). Independent verification is still recommended."
        )
    elif risk_category == "Caution Advised":
        return (
            f"This internship communication shows some concerning patterns "
            f"(risk score: {risk_score}/100). Proceed with caution and verify details carefully."
        )
    else:
        return (
            f"This internship communication shows multiple concerning patterns "
            f"(risk score: {risk_score}/100). Extra caution and thorough verification are strongly advised."
        )


# ---------- MAIN EXPLANATION ENGINE ----------

def generate_explanation(risk_result: Dict[str, Any]) -> Dict[str, Any]:
    details = risk_result.get("details", {})
    risk_category = risk_result.get("risk_category", "Unknown")
    risk_score = risk_result.get("risk_score", 0)

    explanations = []
    explanations.extend(explain_company(details.get("company", [])))
    explanations.extend(explain_payment(details.get("payment", [])))
    explanations.extend(explain_behavior(details.get("behavior", [])))
    explanations.extend(explain_ml(details.get("ml", [])))

    return {
        "risk_category": risk_category,
        "risk_score": risk_score,
        "summary": generate_summary(risk_category, risk_score),
        "explanations": explanations,
        "breakdown": risk_result.get("breakdown", {}),
        "disclaimer": DISCLAIMER
    }
