from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.middleware.auth import get_current_user
from app.services.firebase import db
from datetime import datetime
import uuid

router = APIRouter(prefix="/notepad", tags=["notepad"])

class NoteRequest(BaseModel):
    title: str
    summary: str
    source_conversation_id: str | None = None

class NoteUpdateRequest(BaseModel):
    title: str | None = None
    summary: str | None = None

@router.get("/")
async def list_notes(current_user: dict = Depends(get_current_user)):
    notes = (
        db.collection("notes")
        .where("userId", "==", current_user["uid"])
        .order_by("createdAt", direction="DESCENDING")
        .get()
    )
    return [n.to_dict() for n in notes]

@router.post("/")
async def create_note(body: NoteRequest, current_user: dict = Depends(get_current_user)):
    note_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    data = {
        "noteId": note_id,
        "userId": current_user["uid"],
        "title": body.title,
        "summary": body.summary,
        "sourceConversationId": body.source_conversation_id,
        "createdAt": now,
        "updatedAt": now,
    }
    db.collection("notes").document(note_id).set(data)
    return data

@router.patch("/{note_id}")
async def update_note(
    note_id: str,
    body: NoteUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    ref = db.collection("notes").document(note_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict()["userId"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")

    updates = {k: v for k, v in body.dict().items() if v is not None}
    updates["updatedAt"] = datetime.utcnow().isoformat()
    ref.update(updates)
    return {"message": "Updated"}

@router.delete("/{note_id}")
async def delete_note(note_id: str, current_user: dict = Depends(get_current_user)):
    ref = db.collection("notes").document(note_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict()["userId"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    ref.delete()
    return {"message": "Deleted"}