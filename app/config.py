from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Now we can read each variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
SECRET_KEY = os.getenv("SECRET_KEY")