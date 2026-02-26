import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.config import FIREBASE_SERVICE_ACCOUNT_PATH

cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)

firebase_admin.initialize_app(cred)

db = firestore.client()

def get_user(uid: str):
    """Get a user document from Firestore by UID."""
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None

def create_or_update_user(uid: str, data: dict):
    """Create user on first login, or update existing user."""
    db.collection("users").document(uid).set(data, merge=True)

def verify_firebase_token(id_token: str) -> dict:
    """Verify a Firebase ID token and return the decoded user info."""
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception:
        return None