# app/services/firebase.py

import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.config import get_firebase_credentials

firebase_credentials = get_firebase_credentials()

if not firebase_credentials:
    raise ValueError("Firebase credentials not found.")

# Prevent double initialization (important for reloads)
if not firebase_admin._apps:
    if isinstance(firebase_credentials, dict):
        cred = credentials.Certificate(firebase_credentials)
    else:
        cred = credentials.Certificate(firebase_credentials)

    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_user(uid: str):
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None

def create_or_update_user(uid: str, data: dict):
    db.collection("users").document(uid).set(data, merge=True)

def verify_firebase_token(id_token: str) -> dict:
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception:
        return None