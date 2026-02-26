# app/scheduler.py
# Checks every minute for due reminders and sends notifications

from apscheduler.schedulers.background import BackgroundScheduler
from app.services.firebase import db
from datetime import datetime, timedelta

def check_reminders():
    """Find all due reminders and mark them triggered."""
    now = datetime.utcnow().isoformat()

    # Get all active reminders that are due
    reminders = (
        db.collection("reminders")
        .where("isActive", "==", True)
        .where("triggerAt", "<=", now)
        .get()
    )

    for doc in reminders:
        reminder = doc.to_dict()
        print(f"⏰ Reminder due: {reminder['title']} for user {reminder['userId']}")

        # Calculate next trigger for recurring reminders
        trigger = datetime.fromisoformat(reminder["triggerAt"])
        schedule = reminder["scheduleType"]

        if schedule == "daily":
            next_trigger = (trigger + timedelta(days=1)).isoformat()
            doc.reference.update({"triggerAt": next_trigger})
        elif schedule == "weekly":
            next_trigger = (trigger + timedelta(weeks=1)).isoformat()
            doc.reference.update({"triggerAt": next_trigger})
        elif schedule == "yearly":
            next_trigger = trigger.replace(year=trigger.year + 1).isoformat()
            doc.reference.update({"triggerAt": next_trigger})
        else:
            # "once" — deactivate after firing
            doc.reference.update({"isActive": False})

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()
    print("⏰ Reminder scheduler started")