User Input
   ↓
LLM Intake Agent
   ↓
Planner Agent (CrewAI)
   ↓
Company + Payment + Behavior + ML Agents
   ↓
Risk Engine
   ↓
Explanation Engine
   ↓
Guardrails
   ↓
Streamlit UI Output



safe_intern/
│
├── app.py                          # Streamlit UI entry point
├── requirements.txt                # All Python dependencies
├── README.md                       # Project overview & setup
│
├── config/
│   ├── settings.py                 # Risk thresholds, weights, constants
│   ├── prompts.py                  # LLM intake system prompts
│   └── guardrail_words.py          # Forbidden words (scam, fraud, fake)
│
├── intake/                         # 🔥 LLM-FIRST INPUT HANDLING
│   ├── intake_agent.py             # LLM parses & structures raw input
│   ├── input_router.py             # Routes text / PDF / URL input
│   └── schema.py                   # Structured JSON schema
│
├── agents/                         # CrewAI multi-agent system
│   ├── planner_agent.py            # Controls agent execution flow
│   ├── company_agent.py            # Company legitimacy & email-domain checks
│   ├── payment_agent.py            # Detects fees & payment requests
│   ├── behavior_agent.py           # Detects urgency & manipulation language
│   └── ml_agent.py                 # TF-IDF + Logistic Regression inference
│
├── utils/
│   ├── text_cleaner.py              # Cleans & normalizes text
│   ├── pdf_parser.py               # Extracts text from PDF offer letters
│   ├── url_fetcher.py              # Fetches website text
│   ├── risk_engine.py              # Combines agent scores (0–100)
│   ├── explanation_engine.py       # Generates user-friendly explanations
│   └── guardrails.py               # Enforces ethical output rules
│
├── database/
│   ├── safe_intern.db              # SQLite database file
│   ├── db_init.py                  # Initializes DB tables
│   ├── db_connection.py            # Database connection handler
│   ├── pattern_repository.py       # Access to risk_patterns table
│   ├── company_repository.py       # Access to company_risk_stats table
│   └── metadata_repository.py      # Stores system & model metadata
│
├── ml/
│   ├── train_model.ipynb           # ML training notebook
│   ├── model.pkl                   # Trained Logistic Regression model
│   └── vectorizer.pkl              # TF-IDF vectorizer
│
└── data/
    ├── fake_internships.csv        # Fake internship samples
    └── real_internships.csv        # Genuine internship samples
