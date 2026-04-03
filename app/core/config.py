import os

from dotenv import load_dotenv

load_dotenv()

DB_PATH: str = os.getenv("DB_PATH", "ecommerce.db")
CHAT_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
