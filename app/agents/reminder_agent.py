"""
reminder_agent.py

Time-aware agent responsible for:
- Sending reminders for upcoming events
- Detecting missed events

This agent:
- DOES NOT mutate patient state
- DOES NOT schedule or reschedule
- DOES NOT use LLMs
"""

from datetime import timedelta
from typing import Dict

from app.core.state import PatientState, EventStatus
from app.tools.notification_tools import (
    send_reminder,
    send_missed_alert,
)


class ReminderAgent:
    """
    ReminderAgent observes time and events,
    and triggers notification tools accordingly.
    """

    def __init__(self, reminder_offset_minutes: int = 30):
        """
        reminder_offset_minutes:
        How long before scheduled time to send reminder
        """
        self.reminder_offset = timedelta(minutes=reminder_offset_minutes)

    def run(self, patient_state: PatientState) -> Dict:
        """
        Execute reminder logic.

        Returns a signal dictionary used by LangGraph routing.
        """

        current_time = patient_state.current_time
        signals = {
            "reminder_sent": False,
            "missed_detected": False,
        }

        for event in patient_state.events:
            # Ignore completed or already missed events
            if event.status != EventStatus.SCHEDULED:
                continue

            # 1️⃣ Missed event detection
            if current_time > event.scheduled_time:
                send_missed_alert(
                    patient_id=patient_state.patient_id,
                    event_type=event.event_type,
                    event_id=event.event_id,
                )
                signals["missed_detected"] = True
                continue

            # 2️⃣ Reminder detection
            reminder_time = event.scheduled_time - self.reminder_offset

            if reminder_time <= current_time <= event.scheduled_time:
                send_reminder(
                    patient_id=patient_state.patient_id,
                    event_type=event.event_type,
                    event_id=event.event_id,
                )
                signals["reminder_sent"] = True

        return signals
