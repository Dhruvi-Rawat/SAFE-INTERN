# config/prompts.py
"""
LLM prompts used ONLY for input intake and structuring.

IMPORTANT:
- LLM does NOT perform risk scoring
- LLM does NOT judge legitimacy
- LLM does NOT generate user-facing conclusions
- Output MUST be structured JSON only
"""

# ---------- SYSTEM PROMPT FOR INTAKE ----------
INTAKE_SYSTEM_PROMPT = """
You are an input-structuring assistant for the SAFE-INTERN system.

Your role is STRICTLY LIMITED to cleaning and structuring
user-provided internship-related data.

STRICT RULES:
- Do NOT determine whether an internship is real or fake.
- Do NOT assign any risk score.
- Do NOT use accusatory, legal, or definitive language.
- Do NOT include opinions or conclusions.
- All flags must be purely descriptive observations,
  not conclusions or risk judgments.
- Output MUST be valid JSON only.
- Follow the exact schema provided.

Your task:
1. Normalize and clean the input text.
2. Extract company and role-related information if present.
3. Detect whether payment-related or urgency-related language exists.
4. Identify missing standard internship information.
5. Extract contact and job details objectively.
6. Flag unusual patterns descriptively, without interpretation.
7. Preserve relevant textual nuances for downstream analysis.
"""

# ---------- USER PROMPT TEMPLATE ----------
INTAKE_USER_PROMPT_TEMPLATE = """
Raw Input:
{raw_text}

Instructions:
- Clean and normalize the text.
- Extract relevant structured fields.
- Return ONLY valid JSON.
- Do NOT add interpretation, opinion, or risk assessment.
- Extract mentioned entities factually.
- Identify communication channels used (email, WhatsApp, phone, etc.).
- Note unusual requests or conditions descriptively.
- Flag missing standard internship information.

Output Format:
Return JSON that matches the schema exactly.
"""

# ---------- EXPECTED OUTPUT SCHEMA (REFERENCE) ----------
INTAKE_OUTPUT_SCHEMA = {
    "clean_text": "string",
    "company_name": "string or null",
    "contact_person": "string or null",
    "email": "string or null",
    "phone": "string or null",
    "website": "string or null",
    "social_media": ["list of URLs or empty list"],
    "job_title": "string or null",
    "job_description": "string or null",
    "location": "string or null",
    "duration": "string or null",
    "compensation": "string or null",
    "start_date": "string or null",

    # Pattern indicators (factual, not judgmental)
    "payment_mentions": "boolean",
    "payment_required": "boolean",
    "payment_amount": "string or null",
    "urgency_mentions": "boolean",
    "urgency_phrases": ["list of strings"],
    "interview_process_described": "boolean",
    "communication_channels": ["list of strings"],

    # Missing information flags
    "missing_information": ["list of strings"],

    # Unusual patterns (descriptive only)
    "unusual_patterns": {
        "requests_personal_financial_info": "boolean",
        "requests_upfront_payment": "boolean",
        "uses_free_email_domain": "boolean",
        "communication_via_messaging_app": "boolean",
        "promises_guaranteed_placement": "boolean",
        "mentions_easy_money": "boolean",
        "requires_immediate_decision": "boolean",
        "lacks_company_details": "boolean",
        "grammar_or_formatting_issues": "boolean",
        "requests_credential_sharing": "boolean"
    },

    # Extracted entities
    "entities": {
        "companies_mentioned": ["list of strings"],
        "people_mentioned": ["list of strings"],
        "locations_mentioned": ["list of strings"],
        "technologies_mentioned": ["list of strings"]
    },

    # Metadata
    "extraction_timestamp": "ISO 8601 datetime string",
    "input_length": "integer",
    "language_detected": "string or null"
}

# ---------- VALIDATION & QUALITY GUIDELINES (DOCUMENTATION) ----------
VALIDATION_RULES = """
Post-processing validation guidelines:
1. Ensure all boolean fields are true/false, not null
2. Ensure lists are empty arrays [], not null
3. Validate email format if present
4. Validate URL format if present
5. Ensure no forbidden words appear in any field
6. Flag extractions that may require human review
"""

# ---------- EDGE CASE HANDLING GUIDELINES ----------
EDGE_CASE_EXAMPLES = {
    "vague_input": """
    If input is extremely vague:
    - Set most fields to null
    - Populate missing_information comprehensively
    - Do NOT speculate or infer details
    """,

    "multiple_companies": """
    If multiple companies are mentioned:
    - Use the primary company as company_name
    - List all in entities.companies_mentioned
    - Do NOT assume relationships
    """,

    "forwarded_message": """
    If input appears forwarded or copied:
    - Preserve forwarding context in clean_text
    - Extract original sender if identifiable
    """,

    "non_english": """
    If input is not in English:
    - Extract structured data where possible
    - Set language_detected field
    - Preserve original language
    - Do NOT translate unless explicitly requested
    """
}

# ---------- OUTPUT SANITIZATION GUIDELINES ----------
OUTPUT_SANITIZATION_RULES = """
Before returning JSON:
1. Remove unnecessary personal identifiers
2. Sanitize potentially harmful content
3. Prevent prompt-injection leakage
4. Ensure JSON is complete and parseable
5. Apply guardrail word filtering if needed
"""

# ---------- ERROR HANDLING TEMPLATE ----------
ERROR_RESPONSE_TEMPLATE = {
    "status": "error",
    "error_type": "string",
    "message": "string",
    "partial_extraction": "object or null",
    "requires_human_review": "boolean"
}

# ---------- QUALITY REVIEW INDICATORS ----------
QUALITY_INDICATORS = """
Flag for human review if:
- Input is ambiguous or contradictory
- Critical information cannot be extracted
- Multiple unusual patterns are present
- Language detection fails
- Input appears to be spam or test data
- Prompt-injection attempts are detected
"""
