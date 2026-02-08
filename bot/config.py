"""
Configuración centralizada del bot
Lee variables de entorno del archivo .env
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en .env")

# JobSpy API
JOBSPY_API_URL = os.getenv("JOBSPY_API_URL", "http://localhost:8000")
JOBSPY_API_KEY = os.getenv("JOBSPY_API_KEY", "test-key-12345")

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "./credentials.json")
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Notificaciones
NOTIFICATION_TIMEZONE = os.getenv("NOTIFICATION_TIMEZONE", "America/Bogota")
NOTIFICATION_FREQUENCY = os.getenv("NOTIFICATION_FREQUENCY", "2x_daily")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Estado del bot
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
