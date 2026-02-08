"""
notification_tools.py

Mock notification tools used by ReminderAgent.
These simulate external side effects like email/SMS/calls.

NO real integrations here.
"""

def send_reminder(patient_id: str, event_type: str, event_id: str):
    """
    Simulate sending a reminder notification.
    """
    print(
        f"[NotificationTool] Reminder sent to patient {patient_id} "
        f"for {event_type} (event_id={event_id})"
    )


def send_missed_alert(patient_id: str, event_type: str, event_id: str):
    """
    Simulate alert when an event is missed.
    """
    print(
        f"[NotificationTool] MISSED alert for patient {patient_id} "
        f"for {event_type} (event_id={event_id})"
    )
