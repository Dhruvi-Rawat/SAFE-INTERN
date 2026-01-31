# app.py
import streamlit as st
from datetime import datetime

from intake.input_router import route_input
from intake.intake_agent import run_intake
from agents.planner_agent import run_planner
from utils.risk_engine import calculate_risk
from utils.explanation_engine import generate_explanation
from utils.guardrails import apply_full_guardrails


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SAFE-INTERN",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []  # each: {time, input_preview, risk_score, risk_category}

if "last_output" not in st.session_state:
    st.session_state.last_output = None

if "demo_text" not in st.session_state:
    st.session_state.demo_text = ""


# ---------------- HELPERS ----------------
def score_color(score: int) -> str:
    if score >= 70:
        return "🔴"
    if score >= 40:
        return "🟠"
    return "🟢"


def score_label(score: int) -> str:
    if score >= 70:
        return "High Risk"
    if score >= 40:
        return "Moderate Risk"
    return "Low Risk"


def render_score_card(score: int, category: str, summary: str):
    icon = score_color(score)
    col1, col2 = st.columns([1.2, 2.8])

    with col1:
        st.markdown("### Risk Score")
        st.markdown(f"## {icon} **{score} / 100**")
        st.progress(min(max(score, 0), 100))

    with col2:
        st.markdown("### Risk Category")
        st.markdown(f"## **{category}**")
        st.markdown(summary)


def add_to_history(user_text: str, risk_score: int, risk_category: str):
    preview = user_text.strip().replace("\n", " ")[:90]
    st.session_state.history.insert(
        0,
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "input_preview": preview + ("..." if len(preview) == 90 else ""),
            "risk_score": risk_score,
            "risk_category": risk_category
        }
    )
    st.session_state.history = st.session_state.history[:8]


# ---------------- TOP BAR ----------------
st.markdown(
    """
    <style>
    .big-title {font-size: 40px; font-weight: 800; margin-bottom: 0px;}
    .sub-title {font-size: 16px; opacity: 0.8; margin-top: 0px;}
    .pill {display:inline-block; padding:6px 10px; border-radius:999px; font-size:12px; border:1px solid rgba(255,255,255,0.15); margin-right:6px;}
    .box {padding:14px; border-radius:16px; border:1px solid rgba(255,255,255,0.12);}
    </style>
    """,
    unsafe_allow_html=True
)

left, right = st.columns([2.2, 1])
with left:
    st.markdown('<div class="big-title">🛡️ SAFE-INTERN</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Internship Risk Advisory • Transparent scoring • No accusations</div>', unsafe_allow_html=True)
with right:
    st.markdown(
        """
        <div style="text-align:right;">
          <span class="pill">Text</span>
          <span class="pill">URL</span>
          <span class="pill">PDF</span>
          <span class="pill">Multi-Agent</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ⚙️ Controls")

    show_advanced = st.toggle("Show advanced details", value=True)
    show_history = st.toggle("Show analysis history", value=True)

    st.markdown("---")
    st.markdown("### 🧪 Quick Demo Inputs")

    demo_safe = """Hello,

Next step is an interview scheduled this week.
No payment is required at any stage.

Please apply only through our official website:
https://careers.tcs.com

Regards,
HR Team
"""

    demo_scam = """Congratulations! You are selected.
Pay ₹1999 registration fee via UPI today to confirm your seat.
Only 24 hours left. WhatsApp confirmation required.
http://internship-confirmation-free.xyz
"""

    demo_edge = """Hello candidate,
Your interview is tomorrow. Please confirm attendance today.
No payment is required.
https://jobs.microsoft.com
"""

    if st.button("✅ Load Safe Example"):
        st.session_state.demo_text = demo_safe
    if st.button("🚨 Load Scam Example"):
        st.session_state.demo_text = demo_scam
    if st.button("⚖️ Load Edge Example"):
        st.session_state.demo_text = demo_edge

    st.markdown("---")
    st.markdown("### ℹ️ What this tool does")
    st.caption(
        "SAFE-INTERN provides a **risk advisory score** based on behavioral + technical signals. "
        "It does **not** claim something is a scam — it recommends verification steps."
    )

# ---------------- MAIN TABS ----------------
tab1, tab2, tab3 = st.tabs(["🔎 Analyze", "🧠 How it works", "✅ Safety checklist"])

# ---------------- TAB 1: ANALYZE ----------------
with tab1:
    colA, colB = st.columns([1.6, 1.0])

    with colA:
        st.markdown("### Paste internship communication")
        user_text = st.text_area(
            label="",
            height=260,
            placeholder="Paste internship email / WhatsApp message / offer letter / URL...",
            value=st.session_state.demo_text
        )

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            analyze_button = st.button("Analyze Internship Risk", type="primary", use_container_width=True)
        with c2:
            if st.button("Clear", use_container_width=True):
                st.session_state.demo_text = ""
                st.rerun()
        with c3:
            st.caption("Tip: include the URL + full message for best results.")

    with colB:
        st.markdown("### Live Output")
        if st.session_state.last_output:
            out = st.session_state.last_output
            render_score_card(out["risk_score"], out["risk_category"], out["summary"])
            st.markdown("")

            if show_advanced:
                with st.expander("📌 Key observations", expanded=True):
                    for item in out.get("explanations", []):
                        st.markdown(f"- {item}")

                with st.expander("📊 Breakdown by signal", expanded=True):
                    br = out.get("breakdown", {})
                    for k, v in br.items():
                        st.markdown(f"- **{k.replace('_',' ').title()}**: {v}")

                with st.expander("⚠️ Disclaimer"):
                    st.caption(out.get("disclaimer", ""))

        else:
            st.info("Run an analysis to see results here.")

    # ----- PIPELINE -----
    if analyze_button:
        if not user_text.strip():
            st.warning("Please enter internship-related text to analyze.")
        else:
            with st.spinner("Analyzing communication…"):
                try:
                    routed_text = route_input(text_input=user_text)
                    intake_schema = run_intake(routed_text)

                    # Convert IntakeSchema -> dict (pydantic v1/v2 safe)
                    if hasattr(intake_schema, "model_dump"):
                        intake_data = intake_schema.model_dump()
                    elif hasattr(intake_schema, "dict"):
                        intake_data = intake_schema.dict()
                    elif hasattr(intake_schema, "to_dict"):
                        intake_data = intake_schema.to_dict()
                    else:
                        intake_data = intake_schema

                    agent_results = run_planner(intake_data)
                    risk_result = calculate_risk(agent_results)
                    explanation = generate_explanation(risk_result)
                    safe_output = apply_full_guardrails(explanation)

                    # Store output + history
                    st.session_state.last_output = safe_output
                    add_to_history(user_text, safe_output["risk_score"], safe_output["risk_category"])
                    st.success("Analysis completed ✅")
                    st.rerun()

                except Exception as err:
                    st.error("Something went wrong during analysis.")
                    st.exception(err)

    if show_history:
        st.markdown("### 🕒 Recent analyses")
        if st.session_state.history:
            for h in st.session_state.history:
                st.markdown(
                    f"- **{h['time']}** • {score_color(h['risk_score'])} "
                    f"**{h['risk_score']}** ({h['risk_category']}) — {h['input_preview']}"
                )
        else:
            st.caption("No history yet. Run your first analysis.")

# ---------------- TAB 2: HOW IT WORKS ----------------
with tab2:
    st.markdown("## 🧠 How SAFE-INTERN works")
    st.markdown(
        """
**SAFE-INTERN is a decision-support system**, not a scam detector.

### Agents
- **Company agent:** checks domain/email consistency + suspicious domain patterns
- **Payment agent:** detects fees/UPI/amount pressure
- **Behavior agent:** urgency + manipulation cues (e.g., “no interview required”)
- **ML agent:** text similarity to known fraud patterns (small weight)

### Scoring
- Strong red flags (payment + urgency + manipulation) increase risk  
- Trust signals (no-payment + interview + official careers portal) reduce risk  
- Output is a transparent score with explanations
        """
    )
    st.info("In judging: emphasize **transparency**, **calibration**, and **verification prompts**.")

# ---------------- TAB 3: SAFETY CHECKLIST ----------------
with tab3:
    st.markdown("## ✅ Quick verification checklist (what users should do)")
    st.markdown(
        """
**Before you apply or pay anything:**
1. Verify the company website domain and official careers page  
2. Search the recruiter name + company on LinkedIn  
3. Never pay “registration/training/processing” fees without official proof  
4. Confirm internship details via official email/website, not WhatsApp only  
5. If urgent pressure exists, pause and verify independently  
        """
    )
    st.success("Your tool’s goal: help students **pause + verify**, not panic.")