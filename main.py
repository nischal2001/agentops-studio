"""
main.py

Entry point for Patient Journey Orchestration Agent.
"""

from app.core.state import PatientState , PatientJourneyState
from app.workflows.patient_journey_graph import build_patient_journey_graph


def main():
    patient_state = PatientState(patient_id="P001")

    graph = build_patient_journey_graph()

    result = graph.invoke(
        {"patient_state": patient_state}
    )

    final_state = result["patient_state"]

    print("\nFinal Patient State:")
    print(final_state.current_state.value)

    print("\nState History:")
    for h in final_state.history:
        print(f"{h.from_state.value} → {h.to_state.value} by {h.by}")


if __name__ == "__main__":
    main()
