from dotenv import load_dotenv
import os
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

def get_firebase_credentials():
    # If JSON exists (Render production)
    if FIREBASE_SERVICE_ACCOUNT_JSON:
        return json.loads(FIREBASE_SERVICE_ACCOUNT_JSON)

    # If local file path exists (local dev)
    if FIREBASE_SERVICE_ACCOUNT_PATH:
        return FIREBASE_SERVICE_ACCOUNT_PATH

    return None