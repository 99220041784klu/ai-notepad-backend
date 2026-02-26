from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.middleware.auth import get_current_user
from app.services.ai_service import suggest_reply, summarize_conversation, extract_tasks

router = APIRouter(prefix="/ai", tags=["ai"])


class SuggestRequest(BaseModel):
    messages: list[dict]  # [{"isOwn": bool, "text": str}]

class SummarizeRequest(BaseModel):
    messages: list[dict]  # [{"senderId": str, "text": str}]

class ExtractTasksRequest(BaseModel):
    text: str


@router.post("/suggest")
async def get_suggestion(
    body: SuggestRequest,
    current_user: dict = Depends(get_current_user)  # Must be logged in
):
    """Get an AI-suggested reply based on conversation context."""
    if not body.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    suggestion = suggest_reply(body.messages)
    return {"suggestion": suggestion}


@router.post("/summarize")
async def get_summary(
    body: SummarizeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Summarize a conversation."""
    if len(body.messages) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 messages to summarize")

    summary = summarize_conversation(body.messages)
    return {"summary": summary}


@router.post("/extract-tasks")
async def get_tasks(
    body: ExtractTasksRequest,
    current_user: dict = Depends(get_current_user)
):
    """Extract actionable tasks from a message."""
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")

    tasks = extract_tasks(body.text)
    return {"tasks": tasks}