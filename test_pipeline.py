from agents.planner_agent import run_planner

fake_intake = {
    "raw_text": "Pay ₹1999 registration fee today. Only 24 hours left. WhatsApp confirmation."
}

result = run_planner(fake_intake)

print(result)