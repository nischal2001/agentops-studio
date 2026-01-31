"""
scheduling_agent.py

LLM-based agent responsible for scheduling next steps
(appointments, lab tests, follow-ups).
"""

from langchain_openai import ChatOpenAI
from app.core.state import PatientJourneyState



class SchedulingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

    def decide_next_state(self, patient_state):
        """
        Decide next desired state based on current patient state.
        (Temporary rule-based logic; LLM reasoning can be added later)
        """

        current = patient_state.current_state

        if current == PatientJourneyState.INTAKE_COMPLETED:
            return PatientJourneyState.APPOINTMENT_SCHEDULED

        if current == PatientJourneyState.LAB_TEST_REQUIRED:
            return PatientJourneyState.LAB_TEST_SCHEDULED

        if current == PatientJourneyState.DOCTOR_REVIEW_PENDING:
            return PatientJourneyState.FOLLOW_UP_SCHEDULED

        return None
