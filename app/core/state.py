"""
state.py

This file defines the **canonical patient state model** for the
Patient Journey Orchestration Agent.

Core principles:
- NO LLM usage
- NO business decision logic
- NO tool calls
- Deterministic and auditable
- Single source of truth for patient workflow state

Agents READ this state.
Only validated transitions can MODIFY this state.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional


class PatientJourneyState(Enum):
    """
    Enum representing all valid states in the patient journey.

    States represent FACTS, not intentions.
    """

    NEW_PATIENT = "NEW_PATIENT"

    INTAKE_COMPLETED = "INTAKE_COMPLETED"

    APPOINTMENT_SCHEDULED = "APPOINTMENT_SCHEDULED"
    APPOINTMENT_COMPLETED = "APPOINTMENT_COMPLETED"

    LAB_TEST_REQUIRED = "LAB_TEST_REQUIRED"
    LAB_TEST_SCHEDULED = "LAB_TEST_SCHEDULED"
    LAB_TEST_COMPLETED = "LAB_TEST_COMPLETED"

    DOCTOR_REVIEW_PENDING = "DOCTOR_REVIEW_PENDING"

    FOLLOW_UP_SCHEDULED = "FOLLOW_UP_SCHEDULED"
    FOLLOW_UP_COMPLETED = "FOLLOW_UP_COMPLETED"

    JOURNEY_CLOSED = "JOURNEY_CLOSED"


@dataclass(frozen=True)
class StateTransition:
    """
    Immutable record of a state transition.

    Why immutable?
    - History must never change
    - Enables auditing and replay
    - Critical for regulated workflows
    """

    from_state: PatientJourneyState
    to_state: PatientJourneyState
    by: str  # Agent or system component responsible
    at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PatientState:
    """
    Represents the complete, authoritative state of a patient's journey.

    This is the SINGLE SOURCE OF TRUTH.
    """

    # Unique identifier for the patient
    patient_id: str

    # Current position in the patient journey
    current_state: PatientJourneyState = PatientJourneyState.NEW_PATIENT

    # List of states already completed
    completed_states: List[PatientJourneyState] = field(default_factory=list)

    # Stores important timestamps (appointments, lab tests, follow-ups, etc.)
    timestamps: Dict[str, Optional[datetime]] = field(default_factory=dict)

    # Flags indicate issues or alerts, NOT workflow progress
    flags: Dict[str, bool] = field(default_factory=lambda: {
        "missed": False,
        "overdue": False
    })

    # Append-only transition history for auditing
    history: List[StateTransition] = field(default_factory=list)

    def apply_transition(
        self,
        to_state: PatientJourneyState,
        by: str
    ) -> None:
        """
        Applies a state transition AFTER validation.

        IMPORTANT:
        - This method does NOT validate transitions
        - Validation must happen in validator.py
        """

        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            by=by
        )

        # Record transition history (append-only)
        self.history.append(transition)

        # Mark current state as completed
        self.completed_states.append(self.current_state)

        # Move to the new state
        self.current_state = to_state

    def has_completed(self, state: PatientJourneyState) -> bool:
        """
        Checks whether a given state has already been completed.
        Useful for dependency validation.
        """
        return state in self.completed_states

    def mark_flag(self, flag_name: str) -> None:
        """
        Marks a flag as True.
        Flags signal problems but do NOT advance workflow.
        """
        if flag_name not in self.flags:
            raise ValueError(f"Unknown flag: {flag_name}")

        self.flags[flag_name] = True

    def clear_flag(self, flag_name: str) -> None:
        """
        Clears a previously set flag.
        """
        if flag_name not in self.flags:
            raise ValueError(f"Unknown flag: {flag_name}")

        self.flags[flag_name] = False
