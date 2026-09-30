import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# -----------------------------
# API KEYS
# -----------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

HF_API_KEY = os.getenv("HF_API_KEY", "").strip()


# -----------------------------
# AI MODELS
# -----------------------------

GEMINI_OUTLINE_MODEL = os.getenv(
    "GEMINI_OUTLINE_MODEL",
    "gemini-2.5-flash"
)

GEMINI_STORY_MODEL = os.getenv(
    "GEMINI_STORY_MODEL",
    "gemini-2.5-flash"
)

HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "stabilityai/stable-diffusion-xl-base-1.0"
)


# -----------------------------
# APPLICATION SETTINGS
# -----------------------------

APP_NAME = "ComicCraft"

PANEL_COUNT = 5


# -----------------------------
# DIRECTORIES
# -----------------------------

STATIC_DIR = BASE_DIR / "static"

PANEL_DIR = STATIC_DIR / "panels"

EXPORT_DIR = STATIC_DIR / "exports"

TEMPLATES_DIR = BASE_DIR / "templates"


# Create directories automatically

STATIC_DIR.mkdir(exist_ok=True)

PANEL_DIR.mkdir(parents=True, exist_ok=True)

EXPORT_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATES_DIR.mkdir(exist_ok=True)