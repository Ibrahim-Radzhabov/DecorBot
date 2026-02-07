# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MANAGER_ID = 6241530829
BOT_TOKEN = "7585644905:AAHC8qEHJmh_jFBncUODo4JQhagFllQ3h_U"

BASE_URL = os.getenv("BASE_URL", "https://overpositive-historiographical-marian.ngrok-free.dev") # Твой URL из ngrok
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"
WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8000