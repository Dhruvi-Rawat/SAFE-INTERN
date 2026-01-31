print("test_m1.py started ✅")

from agents.ml_agent import MLAgent
ml = MLAgent()
tests = [
    "Pay ₹1999 registration fee today via UPI to confirm internship.",
    "Apply through our official careers portal. Interview rounds will follow."
]

for t in tests:
    print(ml.run(t))