# agents/company_agent.py
"""
Company agent for SAFE-INTERN using CrewAI.

Responsibilities:
- Check company website availability
- Check presence of basic transparency pages (About / Contact)
- Compare email domain with website domain
- Detect use of free email domains

NO company name verification
NO social media analysis
NO SSL / domain age checks
NO risk scoring
NO accusations
"""

from typing import Dict, Any, List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from crewai import Agent
from crewai.tasks import Task


# ---------- CONSTANTS ----------

FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "icloud.com",
    "aol.com"
}


# ---------- CREWAI AGENT ----------

agent = Agent(
    role="Company Verification Analyst",
    goal="Analyze company legitimacy using website and email consistency signals",
    backstory=(
        "You evaluate observable company legitimacy signals such as "
        "website presence, transparency pages, and email domain consistency. "
        "You do not accuse or confirm fraud."
    ),
    allow_delegation=False,
    verbose=False
)


# ---------- HELPER FUNCTIONS ----------

def normalize_url(url: str) -> str:
    """
    Normalize URL by ensuring scheme is present.
    Example: example.com -> https://example.com
    """
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def extract_domain(url: str) -> str | None:
    """Extract domain from URL"""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "").lower()
    except Exception:
        return None


def extract_email_domain(email: str) -> str | None:
    """Extract domain from email"""
    if not email or "@" not in email:
        return None
    return email.split("@")[-1].lower()


def check_website(url: str) -> Dict[str, bool]:
    """
    Check website reachability and basic transparency pages.
    """
    result = {
        "reachable": False,
        "has_about_page": False,
        "has_contact_page": False
    }

    try:
        # timeout prevents the UI from hanging on slow or dead sites
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return result

        result["reachable"] = True

        soup = BeautifulSoup(response.text, "html.parser")
        links = [a.get("href", "").lower() for a in soup.find_all("a")]

        result["has_about_page"] = any("about" in link for link in links)
        result["has_contact_page"] = any("contact" in link for link in links)

        return result

    except Exception:
        return result


# ---------- MAIN ANALYSIS ----------

def analyze_company(intake_data: Dict[str, Any]) -> Dict[str, Any]:
    observations: List[str] = []

    website = intake_data.get("website")
    email = intake_data.get("email")

    website_domain = None
    email_domain = extract_email_domain(email)

    # ---- Website Checks ----
    if website:
        website = normalize_url(website)
        website_domain = extract_domain(website)

        website_info = check_website(website)

        if website_info["reachable"]:
            observations.append("The company website is reachable.")

            if website_info["has_about_page"]:
                observations.append("The website includes an About section.")
            else:
                observations.append("No About section was found on the website.")

            if website_info["has_contact_page"]:
                observations.append("The website includes a Contact section.")
            else:
                observations.append("No Contact section was found on the website.")
        else:
            observations.append("The provided website could not be reached.")
    else:
        observations.append("No official company website was provided.")

    # ---- Email Domain Checks ----
    if email_domain:
        if email_domain in FREE_EMAIL_DOMAINS:
            observations.append(
                "Communication uses a free email domain rather than a corporate domain."
            )
        else:
            observations.append(
                "A non-free email domain is used for communication."
            )
    else:
        observations.append("No email address was provided for verification.")

    # ---- Domain Consistency ----
    if website_domain and email_domain:
        if website_domain == email_domain:
            observations.append("Email domain matches the website domain.")
        else:
            observations.append("Email domain does not match the website domain.")

    return {
        "website": website,
        "email": email,
        "observations": observations
    }


# ---------- TASK CREATION ----------

def create_task(intake_data: Dict[str, Any]) -> Task:
    analysis = analyze_company(intake_data)

    description = f"""
Analyze the following company-related signals and summarize observations.

Website: {analysis['website']}
Email: {analysis['email']}

Observations:
{chr(10).join(f"- {o}" for o in analysis['observations'])}

Rules:
- Be factual and neutral
- Do NOT accuse or confirm fraud
- Do NOT assign any score
"""

    return Task(
        description=description,
        agent=agent,
        expected_output=(
            "A neutral summary of website availability, "
            "basic transparency, and email domain consistency."
        )
    )
