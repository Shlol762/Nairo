import os
from dotenv import load_dotenv

load_dotenv()

# -- Core Settings --
ENABLED_SENSES = [
    "web",
    # "discord",
    # "email",
]
LOG_LEVEL = "INFO"
LOG_FILE = "logs/nairo.log"

# -- Model and API Keys --
# Loaded from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Add other API keys here if needed

# -- Interpreter Settings --
MODEL_NAME = "gemini/gemini-2.5-flash-preview-09-2025"
INTERPRETER_AUTO_RUN = True

# -- Network Settings --
INTERNET_CHECK_INTERVAL_SECONDS = 60

# -- Database and Memory --
DATABASE_PATH = "nairo.db"
MEMORY_FILE_PATH = "memory.txt"

# -- Web Sense Settings --
WEB_HOST = "127.0.0.1"
WEB_PORT = 5000
