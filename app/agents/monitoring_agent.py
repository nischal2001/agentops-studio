"""
MonitoringAgent

Decides whether the patient journey workflow should continue or stop.
"""

from app.core.state import PatientJourneyState



class MonitoringAgent:
    def decide(self, patient_state) -> str:
        """
        Decide whether the workflow should continue or stop.
        """

        terminal_states = {
            PatientJourneyState.NEW_PATIENT,
            PatientJourneyState.FOLLOW_UP_COMPLETED,
        }

        # Stop if terminal
        if patient_state.current_state in terminal_states:
            return "stop"

        # Stop if no transitions happened
        if not patient_state.history:
            return "stop"

        last = patient_state.history[-1]

        # Stop if no state change
        if last.from_state == last.to_state:
            return "stop"

        return "continue"
