"""
FORTALEZA SHOP AI — configuración central.
Todos los valores sensibles se leen desde variables de entorno.
El modo inicial es TEST y la publicación automática permanece bloqueada.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent
CORE_DIR = BASE_DIR / "core"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"

PRODUCTS_FILE = DATA_DIR / "products.csv"
PUBLISHED_FILE = DATA_DIR / "published.json"
ANALYTICS_FILE = DATA_DIR / "analytics.json"

PROJECT_NAME = "FORTALEZA SHOP AI"
REPOSITORY_NAME = "fortaleza-shop-ai"
BRAND_NAME = "Fortaleza Shop AI"
USERNAME = "@FortalezaShopAI"
COUNTRY = "MX"
LANGUAGE = "es-MX"
TIMEZONE_NAME = "America/Mexico_City"
TIMEZONE = ZoneInfo(TIMEZONE_NAME)

VIDEO_FORMAT = "9:16"
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
MIN_VIDEO_DURATION = 15
MAX_VIDEO_DURATION = 45

PRODUCT_CATEGORIES = [
    "productos_virales",
    "hogar",
    "tecnologia",
    "descubrimientos",
]

VALID_MODES = ("TEST", "REVIEW", "AUTO")
PUBLISH_MODE = os.getenv("PUBLISH_MODE", "TEST").strip().upper()
if PUBLISH_MODE not in VALID_MODES:
    raise ValueError(f"PUBLISH_MODE inválido: {PUBLISH_MODE}. Usa TEST, REVIEW o AUTO.")

# IA externa solo se activa con una decisión explícita; puede generar cargos.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
ENABLE_PAID_AI = os.getenv("ENABLE_PAID_AI", "false").strip().lower() in {"1", "true", "yes"}

TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "").strip()
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "").strip()
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "").strip()
TIKTOK_OPEN_ID = os.getenv("TIKTOK_OPEN_ID", "").strip()
TIKTOK_PUBLISH_ENABLED = False  # Se mantiene desactivado hasta integrar y validar API oficial.

VIDEO_STORAGE_URL = os.getenv("VIDEO_STORAGE_URL", "").strip()
STORAGE_ENABLED = bool(VIDEO_STORAGE_URL)

SCHEDULE = {
    "product_search": "07:00",
    "product_selection": "07:15",
    "script_generation": "07:30",
    "video_generation": "07:45",
    "publication": "08:15",
    "analytics": "21:00",
}

VIDEO_SETTINGS = {
    "width": VIDEO_WIDTH,
    "height": VIDEO_HEIGHT,
    "fps": 30,
    "format": "mp4",
    "codec": "libx264",
    "audio_codec": "aac",
    "max_duration": MAX_VIDEO_DURATION,
    "min_duration": MIN_VIDEO_DURATION,
}

RULES = {
    "avoid_duplicate_products": True,
    "avoid_duplicate_scripts": True,
    "require_valid_affiliate_link": True,
    "require_verified_price": True,
    "require_verified_commission": True,
    "validate_video_before_publish": True,
    "prevent_duplicate_publications": True,
    "stop_on_critical_errors": True,
    "use_original_content": True,
    "require_asset_permission": True,
}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = LOGS_DIR / "fortaleza_shop_ai.log"

def initialize_directories():
    """Crea todas las carpetas esperadas sin borrar datos existentes."""
    directories = [
        CORE_DIR, DATA_DIR, DATA_DIR / "products",
        DATA_DIR / "analytics", DATA_DIR / "product_assets",
        OUTPUT_DIR, OUTPUT_DIR / "videos", OUTPUT_DIR / "images",
        OUTPUT_DIR / "voices", OUTPUT_DIR / "scripts",
        OUTPUT_DIR / "pipeline", OUTPUT_DIR / "assets",
        OUTPUT_DIR / "ready_to_publish", OUTPUT_DIR / "content_plans",
        LOGS_DIR, TEMPLATES_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

@dataclass(frozen=True)
class AppConfig:
    project_name: str = PROJECT_NAME
    repository_name: str = REPOSITORY_NAME
    mode: str = PUBLISH_MODE
    openai_api_key: str = OPENAI_API_KEY
    openai_model: str = OPENAI_MODEL
    enable_paid_ai: bool = ENABLE_PAID_AI
    tiktok_client_key: str = TIKTOK_CLIENT_KEY
    tiktok_client_secret: str = TIKTOK_CLIENT_SECRET
    tiktok_access_token: str = TIKTOK_ACCESS_TOKEN
    tiktok_open_id: str = TIKTOK_OPEN_ID
    video_storage_url: str = VIDEO_STORAGE_URL
    timezone: str = TIMEZONE_NAME

    @property
    def is_test(self):
        return self.mode == "TEST"

    @property
    def is_review(self):
        return self.mode == "REVIEW"

    @property
    def is_auto(self):
        return self.mode == "AUTO"

settings = AppConfig()

def get_system_status():
    return {
        "project": PROJECT_NAME,
        "mode": PUBLISH_MODE,
        "timezone": TIMEZONE_NAME,
        "paid_ai_enabled": ENABLE_PAID_AI,
        "openai_key_configured": bool(OPENAI_API_KEY),
        "tiktok_credentials_configured": all((
            TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET,
            TIKTOK_ACCESS_TOKEN, TIKTOK_OPEN_ID,
        )),
        "storage_configured": STORAGE_ENABLED,
        "automatic_publication": False,
        "note": "La publicación automática está bloqueada hasta integrar y validar una API oficial.",
    }

if __name__ == "__main__":
    initialize_directories()
    for key, value in get_system_status().items():
        print(f"{key}: {value}")
