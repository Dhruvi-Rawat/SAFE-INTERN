# agents/company_agent.py
"""
Company agent for SAFE-INTERN (Rule-based).

Checks:
- Website reachability
- HTTPS usage
- Email domain vs website domain
- Free email usage

NO LLM
NO CrewAI
"""

from urllib.parse import urlparse
import requests

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "icloud.com", "aol.com", "protonmail.com"
}


def _extract_domain(value: str | None) -> str | None:
    if not value:
        return None
    if "@" in value:
        return value.split("@")[-1].lower()
    parsed = urlparse(value if value.startswith("http") else "https://" + value)
    return parsed.netloc.replace("www.", "").lower() or None


def run_company_agent(intake_data: dict) -> dict:
    observations = []

    website = intake_data.get("website")
    email = intake_data.get("email")

    website_domain = _extract_domain(website)
    email_domain = _extract_domain(email)

    # Website check
    if website:
        try:
            response = requests.get(
                website if website.startswith("http") else f"https://{website}",
                timeout=5
            )
            if response.status_code != 200:
                observations.append("Company website is not reachable")
            if not website.startswith("https"):
                observations.append("Company website does not use HTTPS")
        except Exception:
            observations.append("Company website is not reachable")

    # Email checks
    if email_domain:
        if email_domain in FREE_EMAIL_DOMAINS:
            observations.append("Free email domain used for communication")

        if website_domain and email_domain != website_domain:
            observations.append("Email domain does not match website domain")

    if not observations:
        observations.append("No major company legitimacy issues detected")

    return {
        "observations": observations
    }
