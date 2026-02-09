"""
state.py

Canonical patient state model for Patient Journey Orchestration Agent.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List


class PatientJourneyState(Enum):
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
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    MISSED = "missed"


@dataclass
class PatientEvent:
    event_id: str
    event_type: str
    scheduled_time: datetime
    status: EventStatus = EventStatus.SCHEDULED


@dataclass(frozen=True)
class StateTransition:
    from_state: PatientJourneyState
    to_state: PatientJourneyState
    by: str
    at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PatientState:
    patient_id: str
    current_state: PatientJourneyState = PatientJourneyState.NEW_PATIENT
    history: List[StateTransition] = field(default_factory=list)

    # 🕒 Simulated time
    current_time: datetime = field(
        default_factory=lambda: datetime(2025, 1, 1, 9, 0)
    )

    # 📅 Events
    events: List[PatientEvent] = field(default_factory=list)

    # 🚨 Workflow signals (agent communication bus)
    signals: Dict[str, bool] = field(default_factory=dict)

    # -----------------------------
    # State transitions
    # -----------------------------
    def apply_transition(self, to_state: PatientJourneyState, by: str):
        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            by=by
        )
        self.history.append(transition)
        self.current_state = to_state

    # -----------------------------
    # Simulated time control
    # -----------------------------
    def advance_time(self, delta: timedelta):
        self.current_time += delta

    # -----------------------------
    # Event helpers
    # -----------------------------
    def get_due_events(self):
        return [
            e for e in self.events
            if e.status == EventStatus.SCHEDULED
            and e.scheduled_time <= self.current_time
        ]

    # -----------------------------
    # Signal helpers
    # -----------------------------
    def set_signal(self, key: str):
        self.signals[key] = True

    def clear_signal(self, key: str):
        self.signals.pop(key, None)

    # 🔁 Retry counters (per event type)
    retry_counts: Dict[str, int] = field(default_factory=dict)

    def increment_retry(self, event_type: str):
        self.retry_counts[event_type] = self.retry_counts.get(event_type, 0) + 1
    
    
    def get_retry_count(self, event_type: str) -> int:
        return self.retry_counts.get(event_type, 0)
    


    @property
    def completed_states(self) -> set:
        return {t.to_state for t in self.history}
