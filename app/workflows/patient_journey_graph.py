"""
patient_journey_graph.py

Defines the LangGraph workflow for the Patient Journey Orchestration Agent.

Uses:
- LangGraph StateGraph (modern)
- Explicit nodes
- Deterministic state transitions
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.core.state import PatientState, PatientJourneyState
from app.core.validator import validate_transition
from app.agents.scheduling_agent import SchedulingAgent
from app.agents.dependency_agent import DependencyAgent


class JourneyGraphState(TypedDict):
    """
    LangGraph state wrapper.

    LangGraph requires graph state to be immutable-like.
    We pass PatientState inside it.
    """
    patient_state: PatientState



scheduling_agent = SchedulingAgent()

def scheduling_node(state: JourneyGraphState) -> JourneyGraphState:
    """
    LangGraph node: Scheduling Agent
    """

    patient_state = state["patient_state"]

    desired_state = scheduling_agent.decide_next_state(patient_state)

    if desired_state is None:
        # No action needed
        return state

    allowed, reason = validate_transition(
        patient_state=patient_state,
        to_state=desired_state,
        requested_by="SchedulingAgent"
    )

    if not allowed:
        print(f"[SchedulingAgent] Transition blocked: {reason}")
        return state

    # Commit transition (single source of truth)
    patient_state.apply_transition(
        to_state=desired_state,
        by="SchedulingAgent"
    )

    return {"patient_state": patient_state}
def build_patient_journey_graph():
    """
    Builds and returns the LangGraph workflow
    with conditional routing.
    """

    graph = StateGraph(JourneyGraphState)

    # Register nodes
    graph.add_node("dependency_agent", dependency_node)
    graph.add_node("scheduling_agent", scheduling_node)

    # Entry point
    graph.set_entry_point("dependency_agent")

    # Conditional routing from DependencyAgent
    graph.add_conditional_edges(
        "dependency_agent",
        dependency_router,
        {
            "dependencies_ok": "scheduling_agent",
            "dependencies_blocked": END
        }
    )

    # SchedulingAgent always ends (for now)
    graph.add_edge("scheduling_agent", END)

    return graph.compile()


dependency_agent = DependencyAgent()

def dependency_node(state: JourneyGraphState) -> JourneyGraphState:
    """
    DependencyAgent node.

    Performs dependency checks but does NOT mutate state.
    Only returns the state unchanged.
    """

    patient_state = state["patient_state"]

    dependencies_ok = dependency_agent.check_dependencies(patient_state)

    if dependencies_ok:
        print("[DependencyAgent] Dependencies satisfied.")
    else:
        print("[DependencyAgent] Dependencies NOT satisfied.")

    # IMPORTANT: always return state, never a string
    return state



def dependency_router(state: JourneyGraphState) -> str:
    """
    Decides routing based on patient_state inside graph state.
    """

    patient_state = state["patient_state"]

    if dependency_agent.check_dependencies(patient_state):
        return "dependencies_ok"

    return "dependencies_blocked"

