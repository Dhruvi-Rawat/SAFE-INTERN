# agents/company_agent.py
"""
Company agent for SAFE-INTERN (Rule-based).

Checks:
- Extracts domain from website/email/raw_text URL
- HTTPS presence (based on URL scheme, not raw string)
- Email domain vs website domain
- Free email usage
- Suspicious domain patterns (cheap TLDs, keyword stuffing)
- Trusted domain bonus (optional)

NO LLM
NO CrewAI
"""

from urllib.parse import urlparse
import re
import requests

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "icloud.com", "aol.com", "protonmail.com"
}

# Keep small for hackathon demo; you can extend later
TRUSTED_DOMAINS = {
    "tcs.com",
    "microsoft.com",
    "google.com",
    "amazon.com",
    "ibm.com",
    "infosys.com",
}

SUSPICIOUS_TLDS = {".xyz", ".click", ".top", ".live", ".site", ".online", ".work", ".loan"}

URL_REGEX = re.compile(r"(https?://[^\s]+|www\.[^\s]+)", re.IGNORECASE)


def _extract_domain(value: str | None) -> str | None:
    if not value:
        return None
    if "@" in value:
        return value.split("@")[-1].lower()

    v = value.strip()
    if not v.startswith(("http://", "https://")):
        v = "https://" + v  # default scheme for parsing
    parsed = urlparse(v)
    host = parsed.netloc.replace("www.", "").lower()
    return host or None


def _extract_first_url(text: str | None) -> str | None:
    if not text:
        return None
    m = URL_REGEX.search(text)
    if not m:
        return None
    url = m.group(0)
    if url.startswith("www."):
        url = "https://" + url
    return url


def run_company_agent(intake_data: dict) -> dict:
    observations = []
    trust_score = 0

    raw_text = (intake_data.get("raw_text") or "").strip()

    # if website not provided by intake, try to pull from raw text
    website = intake_data.get("website") or _extract_first_url(raw_text)
    email = intake_data.get("email")

    website_domain = _extract_domain(website)
    email_domain = _extract_domain(email)

    # --- Trusted domain bonus ---
    if website_domain:
        # allow subdomains like careers.tcs.com
        base = ".".join(website_domain.split(".")[-2:])
        if base in TRUSTED_DOMAINS:
            observations.append("Recognized well-known company domain (trust signal)")
            trust_score -= 25

    # --- Suspicious TLD check ---
    if website_domain:
        for tld in SUSPICIOUS_TLDS:
            if website_domain.endswith(tld):
                observations.append("Website uses a higher-risk domain extension (TLD)")
                break

    # --- Keyword-stuffed domain check (very common scam pattern) ---
    if website_domain and any(k in website_domain for k in ["internship", "offer", "confirm", "registration", "payment"]):
        observations.append("Domain name contains recruitment/payment keywords (can be misleading)")

    # --- HTTPS check (correct way) ---
    if website:
        # If user typed without scheme, we assume https, so we only flag if explicitly http://
        if website.strip().lower().startswith("http://"):
            observations.append("Website link uses HTTP (not HTTPS)")

    # --- Reachability check (do NOT punish redirects / bot protection) ---
    if website:
        try:
            url = website if website.startswith(("http://", "https://")) else f"https://{website}"
            r = requests.get(url, timeout=5, allow_redirects=True)

            # Only flag true failures
            if r.status_code >= 500:
                observations.append("Website server error (could not verify reliably)")
            # 401/403 often happens for legit sites with bot protection – treat as neutral
        except Exception:
            observations.append("Website could not be reached (network/timeout)")

    # --- Email checks ---
    if email_domain:
        if email_domain in FREE_EMAIL_DOMAINS:
            observations.append("Free email domain used for communication")

        # Compare base domains (handles hr@careers.tcs.com vs tcs.com)
        if website_domain:
            base_web = ".".join(website_domain.split(".")[-2:])
            base_email = ".".join(email_domain.split(".")[-2:])
            if base_web != base_email:
                observations.append("Email domain does not match website domain")

    if not observations:
        observations.append("No major company legitimacy issues detected")

    return {
        "observations": observations,
        "trust_score": trust_score
    }