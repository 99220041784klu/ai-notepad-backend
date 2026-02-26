from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import FRONTEND_URL

from app.routes import auth, chat, ai, reminders, notepad

app = FastAPI(
    title="AI Conversation Notepad API",
    version="1.0.0",
    description="Backend for AI-powered chat and productivity app"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],   
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],            
)

app.include_router(auth.router,      prefix="/v1")
app.include_router(chat.router,      prefix="/v1")
app.include_router(ai.router,        prefix="/v1")
app.include_router(reminders.router, prefix="/v1")
app.include_router(notepad.router,   prefix="/v1")
from app.scheduler import start_scheduler
start_scheduler()
@app.get("/")
def health_check():
    return {"status": "API is running ✅"}