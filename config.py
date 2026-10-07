"""
DTM Repetitor Agent - Konfiguratsiya sozlamalari
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env yuklash
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
REPORTS_DIR = BASE_DIR / "reports"

# Kataloglarni yaratish
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# API va xizmatlar
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "dtm_repetitor.db"))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Fanlar ro'yxati (MVP va to'liq rejim)
SUBJECTS = [
    "Matematika",
    "Fizika",
    "Ona tili va adabiyot",
    "O'zbekiston tarixi",
    "Biologiya",
    "Kimyo",
    "Ingliz tili"
]

MVP_SUBJECTS = ["Matematika", "Fizika"]

# DTM Standartlari
DIAGNOSTIC_QUESTIONS_COUNT = 30
DAILY_PLAN_DEFAULT_COUNT = 20
DTM_MAX_BALL_SUBJECT = 93.0  # 30 savol * 3.1 ball
DTM_PASS_PERCENTAGE = 0.60  # 60% dan past - zaif mavzu
DTM_STRONG_PERCENTAGE = 0.85 # 85% dan yuqori - kuchli mavzu
