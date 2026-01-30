# agents/planner_agent.py
"""
Planner agent for SAFE-INTERN using CrewAI.

Responsibilities:
- Decide which analysis agents should run
- Orchestrate agent execution order
- Return aggregated agent outputs (no scoring here)
"""

from typing import Dict, Any, List

from crewai import Agent, Task, Crew

from agents.company_agent import company_agent
from agents.payment_agent import payment_agent
from agents.behavior_agent import behavior_agent
from agents.ml_agent import ml_agent


# ---------- PLANNER AGENT ----------

planner_agent = Agent(
    role="Analysis Planner",
    goal="Decide which agents to run for internship risk analysis",
    backstory=(
        "You are responsible for orchestrating a multi-agent analysis system. "
        "You do not analyze risk yourself, but decide which specialized agents "
        "should run based on available intake data."
    ),
    allow_delegation=True,
    verbose=False
)


# ---------- PLANNER LOGIC (DETERMINISTIC) ----------

def decide_agents(intake_data: Dict[str, Any]) -> List[str]:
    """
    Decide which agents should be executed.

    Args:
        intake_data: Structured IntakeSchema as dict

    Returns:
        List of agent identifiers
    """

    agents_to_run = ["company", "behavior", "ml"]

    if intake_data.get("payment_mentions"):
        agents_to_run.append("payment")

    return agents_to_run


# ---------- EXECUTION ----------

def run_planner(intake_schema) -> Dict[str, Any]:
    """
    Run planner and execute selected agents.

    Args:
        intake_schema: IntakeSchema object

    Returns:
        Dictionary of agent results
    """

    intake_dict = intake_schema.to_dict()
    selected_agents = decide_agents(intake_dict)

    tasks = []
    agents = []

    if "company" in selected_agents:
        tasks.append(company_agent.create_task(intake_dict))
        agents.append(company_agent.agent)

    if "payment" in selected_agents:
        tasks.append(payment_agent.create_task(intake_dict))
        agents.append(payment_agent.agent)

    if "behavior" in selected_agents:
        tasks.append(behavior_agent.create_task(intake_dict))
        agents.append(behavior_agent.agent)

    if "ml" in selected_agents:
        tasks.append(ml_agent.create_task(intake_dict))
        agents.append(ml_agent.agent)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=False
    )

    results = crew.kickoff()
    return results
