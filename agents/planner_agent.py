from agents import company_agent, payment_agent, behavior_agent
from agents.ml_agent import MLAgent


# -----------------------
# Helper: convert schema → dict
# -----------------------
def _to_dict(obj):
    if hasattr(obj, "model_dump"):   # pydantic v2
        return obj.model_dump()
    if hasattr(obj, "dict"):         # pydantic v1
        return obj.dict()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return obj


# -----------------------
# Planner
# -----------------------
def run_planner(intake_schema):

    intake_data = _to_dict(intake_schema)

    results = {}

    # ALWAYS keep raw text for scoring
    results["raw_text"] = (
        intake_data.get("raw_text", "")
        or intake_data.get("clean_text", "")
        or ""
    )

    results["company"] = company_agent.run_company_agent(intake_data)
    results["payment"] = payment_agent.run_payment_agent(intake_data)
    results["behavior"] = behavior_agent.run_behavior_agent(intake_data)

    text = results["raw_text"]
    results["ml"] = MLAgent().run(text)

    return results