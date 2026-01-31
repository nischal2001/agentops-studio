"""
dependency_agent.py

DependencyAgent checks whether required workflow
prerequisites are satisfied before proceeding.

This agent:
- Reads patient state
- Performs reasoning (can be rule-based or LLM-based)
- Does NOT mutate state
"""

from app.core.state import PatientJourneyState


class DependencyAgent:
    def check_dependencies(self, patient_state) -> bool:
        """
        Returns True if dependencies are satisfied
        for the patient's current workflow step.
        """

        current = patient_state.current_state

        # If doctor review is pending, lab test must be completed
        if current == PatientJourneyState.DOCTOR_REVIEW_PENDING:
            return patient_state.has_completed(
                PatientJourneyState.LAB_TEST_COMPLETED
            )

        # If follow-up is scheduled, appointment must be completed
        if current == PatientJourneyState.FOLLOW_UP_SCHEDULED:
            return patient_state.has_completed(
                PatientJourneyState.APPOINTMENT_COMPLETED
            )

        # Default: no blocking dependencies
        return True
