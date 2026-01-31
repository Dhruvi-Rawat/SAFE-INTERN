# utils/risk_engine.py

def calculate_risk(agent_results: dict) -> dict:
    score = 0
    breakdown = {}

    raw_text = agent_results.get("raw_text", "") or ""
    text = raw_text.lower()

    # --------------------
    # 1) PAYMENT RISK
    # --------------------
    payment_obs = agent_results.get("payment", {}).get("observations", [])
    payment_flag = any(
        ("payment" in o.lower())
        or ("fee" in o.lower())
        or ("upi" in o.lower())
        or ("amount" in o.lower())
        for o in payment_obs
    )
    financial = 45 if payment_flag else 0
    score += financial
    breakdown["financial"] = financial

    # --------------------
    # 2) BEHAVIOR RISK (hard urgency vs scarcity)
    # --------------------
    behavior = agent_results.get("behavior", {})

    # support BOTH schemas (old + new) so your app won’t break
    hard_urgency = behavior.get("hard_urgency_terms", []) or behavior.get("urgency_terms", [])
    scarcity = behavior.get("scarcity_terms", [])
    manipulation = behavior.get("manipulation_terms", [])
    behavior_obs = behavior.get("observations", [])

    pressure = 0
    if hard_urgency:
        pressure += 20          # strong pressure words
    if scarcity:
        pressure += 6           # limited seats is mild, not scam by itself
    if manipulation:
        pressure += 25
    if any("no clear interview" in o.lower() for o in behavior_obs):
        pressure += 10

    pressure = min(45, pressure)
    score += pressure
    breakdown["pressure"] = pressure

    # --------------------
    # 3) COMPANY RISK + TRUST
    # --------------------
    company_obs = agent_results.get("company", {}).get("observations", [])
    company_risk = 0
    if any(("suspicious" in o.lower()) or ("mismatch" in o.lower()) for o in company_obs):
        company_risk = 15

    score += company_risk
    breakdown["company"] = company_risk

    company_trust = agent_results.get("company", {}).get("trust_score", 0)
    score += company_trust
    breakdown["company_trust"] = company_trust  # usually negative for trusted domains

    # --------------------
    # 4) ML RISK (cap it so it can’t dominate)
    # --------------------
    ml_prob = agent_results.get("ml", {}).get("ml_probability", 0.0) or 0.0
    ml_points = int(ml_prob * 20)
    ml_points = min(15, ml_points)  # ✅ CAP at 15
    score += ml_points
    breakdown["ml"] = ml_points

    # --------------------
    # 5) LEGIT STRUCTURE BONUS (expanded to cover your safe examples)
    # --------------------
    structure_bonus = 0

    # interview/process signals
    if any(k in text for k in [
        "interview", "technical interview", "hr discussion", "resume screening",
        "selection process", "screening", "assessment", "shortlisted",
        "online interaction", "interaction with the founders", "call with founders"
    ]):
        structure_bonus += 20  # strong legitimacy structure

    # mentorship / learning signals
    if any(k in text for k in ["mentor", "mentorship", "hands-on learning", "learning and mentorship"]):
        structure_bonus += 8

    # stipend is a soft legitimacy signal
    if "stipend" in text or "₹" in text:
        # only count stipend if it actually says stipend
        if "stipend" in text:
            structure_bonus += 5

    score -= structure_bonus
    breakdown["structure_bonus"] = -structure_bonus

    # --------------------
    # 6) TRUST / GREEN SIGNALS (strong)
    # --------------------
    trust_bonus = 0

    # strongest green flag
    if any(k in text for k in ["no fees", "no fee", "no payment", "no charges", "no registration fee"]):
        trust_bonus += 30

    # official career portal hint
    if "https://" in text and "careers" in text:
        trust_bonus += 10

    # email from company domain (not free email) – mild bonus
    if ("@" in text) and not any(free in text for free in ["@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com"]):
        trust_bonus += 5

    score -= trust_bonus
    breakdown["trust_bonus"] = -trust_bonus

    # clamp
    score = max(0, min(score, 100))

    if score >= 70:
        category = "High Risk"
    elif score >= 40:
        category = "Moderate Risk"
    else:
        category = "Low Risk"

    return {
        "risk_score": score,
        "risk_category": category,
        "breakdown": breakdown
    }