# app.py
"""
SAFE-INTERN Streamlit UI

Pipeline:
User Input
→ input_router
→ intake_agent (LLM / fallback)
→ planner_agent (CrewAI)
→ company + payment + behavior + ml agents
→ risk_engine
→ explanation_engine
→ guardrails
→ UI output
"""

import streamlit as st

# ---------- INTERNAL IMPORTS ----------
from intake.input_router import route_input
from intake.intake_agent import run_intake
from agents.planner_agent import run_planner
from utils.risk_engine import calculate_risk
from utils.explanation_engine import generate_explanation
from utils.guardrails import apply_full_guardrails


# ---------- STREAMLIT CONFIG ----------
st.set_page_config(
    page_title="SAFE-INTERN",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ SAFE-INTERN")
st.caption("Internship Risk Advisory System")

st.markdown(
    """
Paste an internship message, email, offer letter, or job description below.

This system provides **advisory insights only**  
— it does **NOT** make accusations or legal claims.
"""
)

# ---------- USER INPUT ----------
user_text = st.text_area(
    label="Internship Communication",
    height=260,
    placeholder="Paste internship email / WhatsApp message / offer letter text here..."
)

analyze_button = st.button("Analyze Internship Risk")


# ---------- MAIN PIPELINE ----------
if analyze_button:
    if not user_text.strip():
        st.warning("Please enter internship-related text to analyze.")
    else:
        with st.spinner("Analyzing communication…"):
            try:
                # 1️⃣ Input routing (text / url / pdf support)
                routed_text = route_input(text_input=user_text)

                # 2️⃣ Intake agent (LLM or fallback)
                intake_schema = run_intake(routed_text)

                # 3️⃣ Planner + CrewAI agents
                agent_results = run_planner(intake_schema)

                # 4️⃣ Risk engine
                risk_result = calculate_risk(agent_results)

                # 5️⃣ Explanation engine
                explanation = generate_explanation(risk_result)

                # 6️⃣ Guardrails (mandatory)
                safe_output = apply_full_guardrails(explanation)

                # ---------- UI OUTPUT ----------
                st.success("Analysis completed")

                st.markdown("## 🔍 Risk Summary")
                st.markdown(f"**Risk Category:** {safe_output['risk_category']}")
                st.markdown(f"**Risk Score:** {safe_output['risk_score']} / 100")
                st.markdown(safe_output["summary"])

                st.markdown("---")
                st.markdown("## 📌 Key Observations")
                for item in safe_output["explanations"]:
                    st.markdown(f"- {item}")

                st.markdown("---")
                st.markdown("## 📊 Score Breakdown")
                for agent, score in safe_output["breakdown"].items():
                    st.markdown(f"- **{agent.title()}**: {score}")

                st.markdown("---")
                st.markdown("## ⚠️ Disclaimer")
                st.caption(safe_output["disclaimer"])

            except Exception as err:
                st.error("Something went wrong during analysis.")
                st.exception(err)
