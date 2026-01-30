# Central configuration for SAFE-INTERN

# ---------- RISK SCORE LIMITS ----------
TOTAL_MAX_SCORE = 100                 # Final score upper bound
RULE_BASED_MAX_SCORE = 80              # Max from rule-based agents
ML_MAX_SCORE = 20                      # Max from ML agent

# ---------- RISK CATEGORY THRESHOLDS ----------
LOW_RISK_THRESHOLD = 30                # 0–30 → Low
CAUTION_RISK_THRESHOLD = 60            # 31–60 → Caution
HIGH_RISK_THRESHOLD = 100              # 61–100 → High indicators

# ---------- AGENT SCORE CAPS ----------
COMPANY_AGENT_MAX_SCORE = 40           # Company legitimacy impact
PAYMENT_AGENT_MAX_SCORE = 30           # Payment detection impact
BEHAVIOR_AGENT_MAX_SCORE = 30          # Urgency & manipulation impact

# ---------- ML SETTINGS ----------
ML_SCORE_SCALING = 20                  # Probability × 20
ML_MODEL_PATH = "ml/model.pkl"         # Saved ML model
ML_VECTORIZER_PATH = "ml/vectorizer.pkl"  # Saved TF-IDF vectorizer

# ---------- DATABASE ----------
DATABASE_PATH = "database/safe_intern.db"  # SQLite DB location

# ---------- LLM SETTINGS (CREWAI + OPENROUTER) ----------
LLM_ENABLED = True                     # Enable LLM for intake processing
LLM_PROVIDER = "openrouter"            # LLM provider
LLM_MODEL_NAME = "mistralai/mistral-7b-instruct"  # Free-tier friendly model
LLM_TEMPERATURE = 0.0                  # Deterministic output
LLM_MAX_TOKENS = 512                   # Output size limit
LLM_TIMEOUT = 10                       # Timeout in seconds
LLM_JSON_ONLY = True                   # Enforce JSON-only output

# ---------- GENERAL ----------
DEFAULT_LANGUAGE = "en"                # Supported language
WEB_REQUEST_TIMEOUT = 5                # Seconds
