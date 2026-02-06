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
from datetime import datetime, timedelta
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


class EventStatus(str, Enum):
    """
    Status of a scheduled patient event.
    """
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    MISSED = "missed"


@dataclass
class PatientEvent:
    """
    Represents a scheduled event in the patient's journey.
    Examples: appointment, lab test, follow-up
    """
    event_id: str
    event_type: str          # e.g. "appointment", "lab_test", "follow_up"
    scheduled_time: datetime
    status: EventStatus = EventStatus.SCHEDULED


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
    Core domain state for a patient journey.
    Acts as the single source of truth.
    """

    patient_id: str
    current_state: PatientJourneyState = PatientJourneyState.NEW_PATIENT
    history: List[StateTransition] = field(default_factory=list)

    # -----------------------------
    # 🕒 Simulated time (deterministic)
    # -----------------------------
    current_time: datetime = field(
        default_factory=lambda: datetime(2025, 1, 1, 9, 0)
    )

    # -----------------------------
    # 📅 Scheduled events
    # -----------------------------
    events: List[PatientEvent] = field(default_factory=list)

    # -----------------------------
    # State transition handling
    # -----------------------------
    def apply_transition(self, to_state: PatientJourneyState, by: str):
        """
        Apply a validated state transition.
        """

        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            by=by
        )

        self.history.append(transition)
        self.current_state = to_state

    # -----------------------------
    # 🕒 Time control (simulation only)
    # -----------------------------
    def advance_time(self, delta: timedelta):
        """
        Advance simulated time.
        This should ONLY be called by simulation/test runners.
        """
        self.current_time += delta

    # -----------------------------
    # 📅 Event helpers (read-only)
    # -----------------------------
    def get_due_events(self) -> List[PatientEvent]:
        """
        Returns events whose scheduled time has passed
        but are still not completed.
        """
        return [
            event for event in self.events
            if event.status == EventStatus.SCHEDULED
            and event.scheduled_time <= self.current_time
        ]
    @property
    def completed_states(self) -> set:
        """
        Returns the set of states that have already been completed
        in this patient journey.

        Derived from transition history.
        """
        completed = set()

        for transition in self.history:
            completed.add(transition.to_state)

        return completed
