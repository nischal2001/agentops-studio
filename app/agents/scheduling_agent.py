"""
scheduling_agent.py

LLM-based agent responsible for scheduling next steps
(appointments, lab tests, follow-ups).
"""

from langchain_openai import ChatOpenAI
from app.core.state import PatientJourneyState



class SchedulingAgent:
    def __init__(self, use_llm: bool = False):
        """
        SchedulingAgent can operate in:
        - rule-based mode (default, no LLM)
        - LLM-based mode (enabled later)
        """
        self.use_llm = use_llm
        self.llm = None

        if self.use_llm:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0
            )


    def decide_next_state(self, patient_state):
        """
        Decide next desired state based on current patient state.
        (Temporary rule-based logic; LLM reasoning can be added later)
        """

        # Handle missed events (reschedule logic)
        if patient_state.signals.get("missed_event"):
            patient_state.clear_signal("missed_event")
        
            if patient_state.current_state == PatientJourneyState.APPOINTMENT_SCHEDULED:
                return PatientJourneyState.APPOINTMENT_SCHEDULED  # re-schedule
        
            if patient_state.current_state == PatientJourneyState.LAB_TEST_SCHEDULED:
                return PatientJourneyState.LAB_TEST_SCHEDULED
        
            if patient_state.current_state == PatientJourneyState.FOLLOW_UP_SCHEDULED:
                return PatientJourneyState.FOLLOW_UP_SCHEDULED
        

        current = patient_state.current_state

        if current == PatientJourneyState.INTAKE_COMPLETED:
            return PatientJourneyState.APPOINTMENT_SCHEDULED

        if current == PatientJourneyState.LAB_TEST_REQUIRED:
            return PatientJourneyState.LAB_TEST_SCHEDULED

        if current == PatientJourneyState.DOCTOR_REVIEW_PENDING:
            return PatientJourneyState.FOLLOW_UP_SCHEDULED

        return None
