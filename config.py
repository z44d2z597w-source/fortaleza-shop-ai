
"""
FORTALEZA SHOP AI
Archivo central de configuración
"""

import os
from pathlib import Path
from dataclasses import dataclass
from zoneinfo import ZoneInfo


# ==========================================
# RUTAS PRINCIPALES
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

CORE_DIR = BASE_DIR / "core"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"

PRODUCTS_FILE = DATA_DIR / "products.csv"
PUBLISHED_FILE = DATA_DIR / "published.json"
ANALYTICS_FILE = DATA_DIR / "analytics.json"


# ==========================================
# IDENTIDAD DEL NEGOCIO
# ==========================================

PROJECT_NAME = "FORTALEZA SHOP AI"
REPOSITORY_NAME = "fortaleza-shop-ai"

BRAND_NAME = "Fortaleza Shop AI"
USERNAME = "@FortalezaShopAI"

COUNTRY = "MX"
LANGUAGE = "es"
TIMEZONE = ZoneInfo("America/Mexico_City")

VIDEO_FORMAT = "9:16"
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

MIN_VIDEO_DURATION = 15
MAX_VIDEO_DURATION = 45


# ==========================================
# CATEGORÍAS DE PRODUCTOS
# ==========================================

PRODUCT_CATEGORIES = [
    "productos_virales",
    "hogar",
    "tecnologia",
    "descubrimientos",
]


# ==========================================
# MODOS DE FUNCIONAMIENTO
# ==========================================

VALID_MODES = ["TEST", "REVIEW", "AUTO"]

PUBLISH_MODE = os.getenv(
    "PUBLISH_MODE",
    "TEST"
).strip().upper()

if PUBLISH_MODE not in VALID_MODES:
    raise ValueError(
        f"Modo inválido: {PUBLISH_MODE}. "
        f"Utiliza TEST, REVIEW o AUTO."
    )

# La publicación automática requiere autorización.
AUTO_PUBLISH_ENABLED = (
    PUBLISH_MODE == "AUTO"
)


# ==========================================
# OPENAI
# ==========================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4.1-mini"
)


# ==========================================
# TIKTOK
# ==========================================

TIKTOK_CLIENT_KEY = os.getenv(
    "TIKTOK_CLIENT_KEY",
    ""
)

TIKTOK_CLIENT_SECRET = os.getenv(
    "TIKTOK_CLIENT_SECRET",
    ""
)

TIKTOK_ACCESS_TOKEN = os.getenv(
    "TIKTOK_ACCESS_TOKEN",
    ""
)

TIKTOK_OPEN_ID = os.getenv(
    "TIKTOK_OPEN_ID",
    ""
)

TIKTOK_PUBLISH_ENABLED = False

# Se habilitará únicamente cuando exista
# autorización oficial y configuración validada.


# ==========================================
# ALMACENAMIENTO EXTERNO
# ==========================================

VIDEO_STORAGE_URL = os.getenv(
    "VIDEO_STORAGE_URL",
    ""
)

STORAGE_ENABLED = bool(VIDEO_STORAGE_URL)


# ==========================================
# PROGRAMACIÓN DIARIA
# ==========================================

SCHEDULE = {
    "product_search": "07:00",
    "product_selection": "07:15",
    "script_generation": "07:30",
    "video_generation": "07:45",
    "publication": "08:15",
    "analytics": "21:00",
}


# ==========================================
# CONFIGURACIÓN DE VIDEOS
# ==========================================

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


# ==========================================
# REGLAS DEL NEGOCIO
# ==========================================

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
}


# ==========================================
# SISTEMA DE REGISTROS
# ==========================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
).upper()

LOG_FILE = LOGS_DIR / "fortaleza_shop_ai.log"


# ==========================================
# INICIALIZACIÓN DE CARPETAS
# ==========================================

def initialize_directories():
    """
    Crea las carpetas necesarias del proyecto.
    """

    directories = [
        CORE_DIR,
        DATA_DIR,
        OUTPUT_DIR,
        LOGS_DIR,
        TEMPLATES_DIR,
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True
        )


# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================

@dataclass(frozen=True)
class AppConfig:

    project_name: str = PROJECT_NAME
    repository_name: str = REPOSITORY_NAME

    mode: str = PUBLISH_MODE

    openai_api_key: str = OPENAI_API_KEY
    openai_model: str = OPENAI_MODEL

    tiktok_client_key: str = TIKTOK_CLIENT_KEY
    tiktok_client_secret: str = TIKTOK_CLIENT_SECRET
    tiktok_access_token: str = TIKTOK_ACCESS_TOKEN
    tiktok_open_id: str = TIKTOK_OPEN_ID

    video_storage_url: str = VIDEO_STORAGE_URL

    timezone: str = "America/Mexico_City"

    @property
    def is_test(self):
        return self.mode == "TEST"

    @property
    def is_review(self):
        return self.mode == "REVIEW"

    @property
    def is_auto(self):
        return self.mode == "AUTO"


# Configuración compartida
settings = AppConfig()


# ==========================================
# VERIFICACIÓN INICIAL
# ==========================================

def get_system_status():

    return {
        "project": PROJECT_NAME,
        "mode": PUBLISH_MODE,
        "timezone": "America/Mexico_City",
        "openai_configured": bool(OPENAI_API_KEY),
        "tiktok_configured": all([
            TIKTOK_CLIENT_KEY,
            TIKTOK_CLIENT_SECRET,
            TIKTOK_ACCESS_TOKEN,
            TIKTOK_OPEN_ID,
        ]),
        "storage_configured": STORAGE_ENABLED,
        "automatic_publication": (
            AUTO_PUBLISH_ENABLED
            and TIKTOK_PUBLISH_ENABLED
        ),
    }


if __name__ == "__main__":

    initialize_directories()

    print("=" * 45)
    print(PROJECT_NAME)
    print("CONFIGURACIÓN DEL SISTEMA")
    print("=" * 45)

    for key, value in get_system_status().items():
        print(f"{key}: {value}")

    print("=" * 45)
    print("Configuración cargada correctamente.")
