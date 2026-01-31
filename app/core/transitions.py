"""
transitions.py

This file defines ALL allowed state transitions
for the Patient Journey Orchestration Agent.

Core principles:
- Deterministic (no LLMs)
- Explicit (no hidden logic)
- Centralized (single source of transition truth)

If a transition is not defined here,
it is NOT allowed in the system.
"""

from typing import Dict, Set
from app.core.state import PatientJourneyState


# -------------------------------------------------------------------
# ALLOWED STATE TRANSITIONS
# -------------------------------------------------------------------
# Each key represents a FROM state.
# The value is a set of states that are allowed to transition TO.
# -------------------------------------------------------------------

ALLOWED_TRANSITIONS: Dict[
    PatientJourneyState,
    Set[PatientJourneyState]
] = {

    PatientJourneyState.NEW_PATIENT: {
        PatientJourneyState.INTAKE_COMPLETED
    },

    PatientJourneyState.INTAKE_COMPLETED: {
        PatientJourneyState.APPOINTMENT_SCHEDULED
    },

    PatientJourneyState.APPOINTMENT_SCHEDULED: {
        PatientJourneyState.APPOINTMENT_COMPLETED
    },

    PatientJourneyState.APPOINTMENT_COMPLETED: {
        PatientJourneyState.LAB_TEST_REQUIRED,
        PatientJourneyState.FOLLOW_UP_SCHEDULED
    },

    PatientJourneyState.LAB_TEST_REQUIRED: {
        PatientJourneyState.LAB_TEST_SCHEDULED
    },

    PatientJourneyState.LAB_TEST_SCHEDULED: {
        PatientJourneyState.LAB_TEST_COMPLETED
    },

    PatientJourneyState.LAB_TEST_COMPLETED: {
        PatientJourneyState.DOCTOR_REVIEW_PENDING
    },

    PatientJourneyState.DOCTOR_REVIEW_PENDING: {
        PatientJourneyState.FOLLOW_UP_SCHEDULED
    },

    PatientJourneyState.FOLLOW_UP_SCHEDULED: {
        PatientJourneyState.FOLLOW_UP_COMPLETED
    },

    PatientJourneyState.FOLLOW_UP_COMPLETED: {
        PatientJourneyState.JOURNEY_CLOSED
    },

    # Terminal state: no transitions allowed
    PatientJourneyState.JOURNEY_CLOSED: set(),
}


# -------------------------------------------------------------------
# PREREQUISITE STATES
# -------------------------------------------------------------------
# Some transitions require that certain states
# must have been completed earlier.
# -------------------------------------------------------------------

PREREQUISITE_STATES: Dict[
    PatientJourneyState,
    Set[PatientJourneyState]
] = {

    # Follow-up cannot be scheduled unless appointment is completed
    PatientJourneyState.FOLLOW_UP_SCHEDULED: {
        PatientJourneyState.APPOINTMENT_COMPLETED
    },

    # Lab test scheduling requires doctor to request it
    PatientJourneyState.LAB_TEST_SCHEDULED: {
        PatientJourneyState.LAB_TEST_REQUIRED
    },

    # Doctor review requires lab test completion
    PatientJourneyState.DOCTOR_REVIEW_PENDING: {
        PatientJourneyState.LAB_TEST_COMPLETED
    },
}


# -------------------------------------------------------------------
# HELPER FUNCTIONS (READ-ONLY)
# -------------------------------------------------------------------

def is_transition_allowed(
    from_state: PatientJourneyState,
    to_state: PatientJourneyState
) -> bool:
    """
    Checks whether a transition from `from_state` to `to_state`
    is defined as allowed.

    This does NOT check prerequisites.
    """
    return to_state in ALLOWED_TRANSITIONS.get(from_state, set())


def get_prerequisites(
    to_state: PatientJourneyState
) -> Set[PatientJourneyState]:
    """
    Returns prerequisite states required before transitioning
    into `to_state`.
    """
    return PREREQUISITE_STATES.get(to_state, set())
