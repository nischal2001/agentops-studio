"""
validator.py

This file implements the **transition validation engine** for the
Patient Journey Orchestration Agent.

Responsibilities:
- Validate whether a requested state transition is legal
- Enforce allowed transitions
- Enforce prerequisite completion
- Prevent regressions or invalid jumps

IMPORTANT:
- No LLM usage
- No state mutation
- Pure validation logic

Agents REQUEST transitions.
This validator DECIDES whether they are allowed.
"""

from typing import Tuple
from app.core.state import PatientState, PatientJourneyState
from app.core.transitions import (
    is_transition_allowed,
    get_prerequisites,
)


# -------------------------------------------------------------------
# VALIDATION RESULT TYPE
# -------------------------------------------------------------------

ValidationResult = Tuple[bool, str]
# (allowed, message)


# -------------------------------------------------------------------
# TRANSITION VALIDATOR
# -------------------------------------------------------------------

def validate_transition(
    patient_state: PatientState,
    to_state: PatientJourneyState,
    requested_by: str,
) -> ValidationResult:
    """
    Validates whether a transition to `to_state` is allowed
    for the given patient_state.

    Returns:
        (True, "OK") if allowed
        (False, "Reason") if blocked
    """

    current_state = patient_state.current_state

    # ---------------------------------------------------------------
    # Rule 1: Prevent no-op transitions
    # ---------------------------------------------------------------
    if current_state == to_state:
        return False, "No-op transition is not allowed"

    # ---------------------------------------------------------------
    # Rule 2: Check if transition is explicitly allowed
    # ---------------------------------------------------------------
    if not is_transition_allowed(current_state, to_state):
        return (
            False,
            f"Transition {current_state.value} → {to_state.value} is not allowed"
        )

    # ---------------------------------------------------------------
    # Rule 3: Check prerequisite states
    # ---------------------------------------------------------------
    prerequisites = get_prerequisites(to_state)

    for required_state in prerequisites:
        if not patient_state.has_completed(required_state):
            return (
                False,
                f"Missing prerequisite: {required_state.value}"
            )

    # ---------------------------------------------------------------
    # Rule 4: Prevent backward transitions (regressions)
    # ---------------------------------------------------------------
    if to_state in patient_state.completed_states:
        return (
            False,
            f"State regression not allowed: {to_state.value} already completed"
        )

    # ---------------------------------------------------------------
    # Rule 5: Terminal state protection
    # ---------------------------------------------------------------
    if current_state == PatientJourneyState.JOURNEY_CLOSED:
        return False, "No transitions allowed after JOURNEY_CLOSED"

    # ---------------------------------------------------------------
    # All checks passed
    # ---------------------------------------------------------------
    return True, "Transition validated successfully"
