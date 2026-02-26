from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.middleware.auth import get_current_user
from app.services.firebase import db
from datetime import datetime
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])

class NewConversationRequest(BaseModel):
    recipient_email: str  # Search for user by Gmail

class NewMessageRequest(BaseModel):
    text: str
    ai_suggested: bool = False  

@router.get("/search")
async def search_user(email: str, current_user: dict = Depends(get_current_user)):
    """Find a user by their Gmail address."""
    users = db.collection("users").where("email", "==", email).limit(1).get()
    results = [u.to_dict() for u in users]

    if not results:
        raise HTTPException(status_code=404, detail="User not found")

    # Don't return your own profile
    if results[0]["uid"] == current_user["uid"]:
        raise HTTPException(status_code=400, detail="Cannot chat with yourself")

    return results[0]


@router.get("/conversations")
async def list_conversations(current_user: dict = Depends(get_current_user)):
    """Get all conversations for the logged-in user."""
    uid = current_user["uid"]
    convs = (
        db.collection("conversations")
        .where("participants", "array_contains", uid)
        .order_by("lastMessageAt", direction="DESCENDING")
        .limit(50)
        .get()
    )
    return [c.to_dict() for c in convs]


@router.post("/conversations")
async def start_conversation(
    body: NewConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start a new conversation with a user found by email."""
    # Find recipient
    users = db.collection("users").where("email", "==", body.recipient_email).limit(1).get()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")

    recipient = users[0].to_dict()
    uid = current_user["uid"]
    recipient_uid = recipient["uid"]

    # Check if conversation already exists between these two users
    existing = (
        db.collection("conversations")
        .where("participants", "array_contains", uid)
        .get()
    )
    for conv in existing:
        data = conv.to_dict()
        if recipient_uid in data.get("participants", []):
            return data  # Return the existing conversation

    # Create a new conversation document
    conv_id = str(uuid.uuid4())
    conv_data = {
        "conversationId": conv_id,
        "participants": [uid, recipient_uid],
        "type": "known",
        "lastMessage": "",
        "lastMessageAt": datetime.utcnow().isoformat(),
        "createdAt": datetime.utcnow().isoformat(),
    }
    db.collection("conversations").document(conv_id).set(conv_data)
    return conv_data


@router.get("/conversations/{conv_id}/messages")
async def get_messages(conv_id: str, current_user: dict = Depends(get_current_user)):
    """Get messages in a conversation."""
    # Security check: user must be a participant
    conv = db.collection("conversations").document(conv_id).get()
    if not conv.exists:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user["uid"] not in conv.to_dict().get("participants", []):
        raise HTTPException(status_code=403, detail="Access denied")

    messages = (
        db.collection("conversations").document(conv_id)
        .collection("messages")
        .order_by("timestamp")
        .limit(100)
        .get()
    )
    return [m.to_dict() for m in messages]


@router.post("/conversations/{conv_id}/messages")
async def send_message(
    conv_id: str,
    body: NewMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a message in a conversation."""
    uid = current_user["uid"]

    # Security check
    conv_ref = db.collection("conversations").document(conv_id)
    conv = conv_ref.get()
    if not conv.exists or uid not in conv.to_dict().get("participants", []):
        raise HTTPException(status_code=403, detail="Access denied")

    # Create the message
    msg_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    msg_data = {
        "messageId": msg_id,
        "senderId": uid,
        "text": body.text,
        "aiSuggested": body.ai_suggested,
        "timestamp": now,
        "readBy": [uid],
    }

    # Save message as subcollection
    conv_ref.collection("messages").document(msg_id).set(msg_data)

    # Update conversation preview
    conv_ref.update({
        "lastMessage": body.text[:50],  # First 50 chars as preview
        "lastMessageAt": now,
    })

    return msg_data