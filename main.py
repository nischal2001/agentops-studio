"""
main.py — TEST RUNNER
"""

from datetime import timedelta
from app.core.state import (
    PatientState,
    PatientEvent,
    PatientJourneyState,
)
from app.workflows.patient_journey_graph import build_patient_journey_graph


def run_test(test_name: str, patient_state: PatientState):
    print(f"\n===== {test_name} =====")
    graph = build_patient_journey_graph()
    result = graph.invoke({"patient_state": patient_state})

    final_state = result["patient_state"]

    print("Final State:", final_state.current_state.value)
    print("History:")
    for h in final_state.history:
        print(f"{h.from_state.value} → {h.to_state.value} by {h.by}")
    print("Signals:", final_state.signals)
    print("Events:", final_state.events)


def main():
    # 🧪 Test 1: Reminder only
    ps1 = PatientState(
        patient_id="P001",
        current_state=PatientJourneyState.APPOINTMENT_SCHEDULED,
    )
    ps1.events.append(
        PatientEvent(
            event_id="EVT-001",
            event_type="appointment",
            scheduled_time=ps1.current_time + timedelta(minutes=20),
        )
    )
    run_test("TEST 1 — Reminder only", ps1)

    # 🧪 Test 2: Missed → reschedule
    ps2 = PatientState(
        patient_id="P002",
        current_state=PatientJourneyState.APPOINTMENT_SCHEDULED,
    )
    ps2.events.append(
        PatientEvent(
            event_id="EVT-002",
            event_type="appointment",
            scheduled_time=ps2.current_time - timedelta(minutes=10),
        )
    )
    run_test("TEST 2 — Missed → Reschedule", ps2)

    # 🧪 Test 3: No events
    ps3 = PatientState(
        patient_id="P003",
        current_state=PatientJourneyState.NEW_PATIENT,
    )
    run_test("TEST 3 — No events", ps3)


if __name__ == "__main__":
    main()
