"""
patient_journey_graph.py

Defines the LangGraph workflow for the Patient Journey Orchestration Agent.

Core principles:
- Nodes ALWAYS return state dicts
- Routers control flow (strings)
- State mutations happen only via validated transitions
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.core.state import PatientState
from app.core.validator import validate_transition

from app.agents.scheduling_agent import SchedulingAgent
from app.agents.dependency_agent import DependencyAgent
from app.agents.monitoring_agent import MonitoringAgent
from app.agents.reminder_agent import ReminderAgent


# ---------------------------------------------------------------------
# LangGraph State Wrapper
# ---------------------------------------------------------------------

class JourneyGraphState(TypedDict):
    """
    LangGraph-compatible state wrapper.
    """
    patient_state: PatientState


# ---------------------------------------------------------------------
# Agent Instances (singletons)
# ---------------------------------------------------------------------

scheduling_agent = SchedulingAgent()
dependency_agent = DependencyAgent()
monitoring_agent = MonitoringAgent()
reminder_agent = ReminderAgent()


# ---------------------------------------------------------------------
# Scheduling Agent Node
# ---------------------------------------------------------------------

def scheduling_node(state: JourneyGraphState) -> JourneyGraphState:
    """
    SchedulingAgent node.

    Decides and commits next valid patient state transition.
    """

    patient_state = state["patient_state"]

    desired_state = scheduling_agent.decide_next_state(patient_state)

    if desired_state is None:
        return state

    allowed, reason = validate_transition(
        patient_state=patient_state,
        to_state=desired_state,
        requested_by="SchedulingAgent"
    )

    if not allowed:
        print(f"[SchedulingAgent] Transition blocked: {reason}")
        return state

    patient_state.apply_transition(
        to_state=desired_state,
        by="SchedulingAgent"
    )

    return {"patient_state": patient_state}


# ---------------------------------------------------------------------
# Dependency Agent Node + Router
# ---------------------------------------------------------------------

def dependency_node(state: JourneyGraphState) -> JourneyGraphState:
    """
    DependencyAgent node.

    Performs dependency checks but NEVER mutates state.
    """

    patient_state = state["patient_state"]

    if dependency_agent.check_dependencies(patient_state):
        print("[DependencyAgent] Dependencies satisfied.")
    else:
        print("[DependencyAgent] Dependencies NOT satisfied.")

    return state


def dependency_router(state: JourneyGraphState) -> str:
    """
    Routes based on dependency check result.
    """

    if dependency_agent.check_dependencies(state["patient_state"]):
        return "dependencies_ok"

    return "dependencies_blocked"


# ---------------------------------------------------------------------
# Reminder Agent Node
# ---------------------------------------------------------------------

def reminder_node(state: JourneyGraphState) -> JourneyGraphState:
    """
    ReminderAgent node.

    Sends reminders / detects misses.
    Does NOT mutate patient state.
    """

    patient_state = state["patient_state"]

    signals = reminder_agent.run(patient_state)

    if signals.get("missed_detected"):
        print("[ReminderAgent] Missed event detected.")

    if signals.get("reminder_sent"):
        print("[ReminderAgent] Reminder sent.")

    return state


# ---------------------------------------------------------------------
# Monitoring Agent Node + Router
# ---------------------------------------------------------------------

def monitoring_node(state: JourneyGraphState) -> JourneyGraphState:
    """
    MonitoringAgent node.

    Evaluates workflow health.
    NEVER returns routing decisions.
    """

    decision = monitoring_agent.decide(state["patient_state"])

    if decision == "continue":
        print("[MonitoringAgent] Workflow still active.")
    else:
        print("[MonitoringAgent] Workflow halted.")

    return state


def monitoring_router(state: JourneyGraphState) -> str:
    """
    Controls graph flow based on MonitoringAgent decision.
    """
    return monitoring_agent.decide(state["patient_state"])


# ---------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------

def build_patient_journey_graph():
    """
    Builds and compiles the LangGraph workflow.
    """

    graph = StateGraph(JourneyGraphState)

    # Register nodes
    graph.add_node("dependency_agent", dependency_node)
    graph.add_node("scheduling_agent", scheduling_node)
    graph.add_node("reminder_agent", reminder_node)
    graph.add_node("monitoring_agent", monitoring_node)

    # Entry point
    graph.set_entry_point("dependency_agent")

    # Dependency → Scheduling
    graph.add_conditional_edges(
        "dependency_agent",
        dependency_router,
        {
            "dependencies_ok": "scheduling_agent",
            "dependencies_blocked": END,
        },
    )

    # Scheduling → Reminder
    graph.add_edge("scheduling_agent", "reminder_agent")

    # Reminder → Monitoring
    graph.add_edge("reminder_agent", "monitoring_agent")

    # Monitoring → Loop or End
    graph.add_conditional_edges(
        "monitoring_agent",
        monitoring_router,
        {
            "continue": "dependency_agent",
            "stop": END,
        },
    )

    return graph.compile()
