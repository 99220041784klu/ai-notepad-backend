from fastapi import Request, HTTPException
from app.services.firebase import verify_firebase_token

async def get_current_user(request: Request) -> dict:
    """
    Extract and verify the Bearer token from the request header.
    Used as a dependency in protected routes.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = auth_header.split(" ")[1]

    user = verify_firebase_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"uid": user["uid"], "email": user.get("email")}