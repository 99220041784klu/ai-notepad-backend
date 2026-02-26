from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.middleware.auth import get_current_user
from app.services.firebase import db
from datetime import datetime
import uuid

router = APIRouter(prefix="/reminders", tags=["reminders"])

class ReminderRequest(BaseModel):
    title: str
    body: str = ""
    schedule_type: str  # "once", "daily", "weekly", "yearly"
    trigger_at: str     # ISO date string like "2025-06-15T09:00:00"
    source_conversation_id: str | None = None

@router.get("/")
async def list_reminders(current_user: dict = Depends(get_current_user)):
    """Get all reminders for the logged-in user."""
    uid = current_user["uid"]
    reminders = (
        db.collection("reminders")
        .where("userId", "==", uid)
        .where("isActive", "==", True)
        .get()
    )
    return [r.to_dict() for r in reminders]

@router.post("/")
async def create_reminder(
    body: ReminderRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new reminder."""
    rem_id = str(uuid.uuid4())
    data = {
        "reminderId": rem_id,
        "userId": current_user["uid"],
        "title": body.title,
        "body": body.body,
        "scheduleType": body.schedule_type,
        "triggerAt": body.trigger_at,
        "isActive": True,
        "sourceConversationId": body.source_conversation_id,
        "createdAt": datetime.utcnow().isoformat(),
    }
    db.collection("reminders").document(rem_id).set(data)
    return data

@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a reminder (only the owner can delete)."""
    ref = db.collection("reminders").document(reminder_id)
    doc = ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if doc.to_dict()["userId"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")

    ref.delete()
    return {"message": "Deleted"}