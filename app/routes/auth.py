from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.middleware.auth import get_current_user
from app.services.firebase import verify_firebase_token, create_or_update_user, get_user
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    id_token: str  

class ProfileUpdateRequest(BaseModel):
    display_name: str | None = None
    is_anonymous_enabled: bool | None = None


@router.post("/login")
async def login(body: LoginRequest):
    """
    Called right after Google Sign-In on the frontend.
    Verifies the Firebase token and creates/updates the user in Firestore.
    """
    user = verify_firebase_token(body.id_token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Save user info to Firestore
    user_data = {
        "uid": user["uid"],
        "email": user.get("email"),
        "displayName": user.get("name", ""),
        "photoURL": user.get("picture", ""),
        "isAnonymousEnabled": False,
        "createdAt": datetime.utcnow().isoformat(),
    }
    create_or_update_user(user["uid"], user_data)

    return {"message": "Login successful", "user": user_data}


@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get the logged-in user's profile."""
    user = get_user(current_user["uid"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/profile")
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update display name or anonymous chat setting."""
    updates = body.dict(exclude_none=True)  # Only include fields that were sent
    if updates:
        create_or_update_user(current_user["uid"], updates)
    return {"message": "Profile updated"}