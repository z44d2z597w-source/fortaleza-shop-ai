
"""
================================================
FORTALEZA SHOP AI
PRODUCT FINDER
Buscador y administrador de productos
================================================

Funciones:
- Consultar fuentes de productos autorizadas.
- Importar productos desde archivos JSON.
- Validar información comercial.
- Detectar duplicados.
- Organizar productos por categoría.
- Guardar el catálogo en CSV.

No realiza scraping de tiendas ni inventa precios,
comisiones o enlaces.
"""

import csv
import json
import logging
import os
import re
import hashlib
import math

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

import config


# =================================================
# CONFIGURACIÓN
# =================================================

logger = logging.getLogger("FORTALEZA_SHOP_AI.PRODUCT_FINDER")

PRODUCTS_FILE = config.PRODUCTS_FILE

PRODUCT_FIELDS = [
    "product_id",
    "name",
    "category",
    "store",
    "seller",
    "price_mxn",
    "commission_percent",
    "product_url",
    "affiliate_url",
    "source",
    "source_id",
    "verified_at",
    "status",
]

VALID_CATEGORIES = set(config.PRODUCT_CATEGORIES)

REQUEST_TIMEOUT = 20

MAX_PRODUCTS_PER_FEED = 200


# =================================================
# INICIALIZACIÓN
# =================================================

def initialize_catalog():
    """
    Crea el catálogo CSV si todavía no existe.
    """

    config.initialize_directories()

    if not PRODUCTS_FILE.exists():

        with open(
            PRODUCTS_FILE,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=PRODUCT_FIELDS
            )

            writer.writeheader()

        logger.info("Catálogo de productos creado.")


# =================================================
# IDENTIFICADOR ÚNICO
# =================================================

def generate_product_id(name, source_id=""):
    """
    Genera un identificador estable para cada producto.
    """

    raw = f"{name.strip().lower()}|{source_id.strip()}"

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:16]


# =================================================
# VALIDACIÓN DE ENLACES
# =================================================

def valid_url(url):
    """
    Comprueba que el enlace sea HTTPS y tenga dominio.
    """

    if not isinstance(url, str):
        return False

    try:

        parsed = urlparse(url.strip())

        return (
            parsed.scheme == "https"
            and bool(parsed.netloc)
            and " " not in url
        )

    except Exception:

        return False


# =================================================
# VALIDACIÓN NUMÉRICA
# =================================================

def clean_number(value, minimum=0, maximum=None):
    """
    Convierte valores numéricos sin inventar información.
    """

    if value is None or value == "":
        return ""

    try:

        number = float(value)

        if not math.isfinite(number) or number < minimum:
            return ""

        if maximum is not None and number > maximum:
            return ""

        return round(number, 2)

    except (ValueError, TypeError):

        return ""


# =================================================
# NORMALIZACIÓN
# =================================================

def normalize_product(raw, source_name="manual"):
    """
    Normaliza un producto recibido desde una fuente.
    """

    if not isinstance(raw, dict):
        return None

    name = str(
        raw.get("name", "")
    ).strip()

    if not name or len(name) > 200:
        return None

    category = str(
        raw.get("category", "")
    ).strip().lower()

    if category not in VALID_CATEGORIES:
        return None

    product_url = str(
        raw.get("product_url", "")
    ).strip()

    affiliate_url = str(
        raw.get("affiliate_url", "")
    ).strip()

    if product_url and not valid_url(product_url):
        product_url = ""

    if affiliate_url and not valid_url(affiliate_url):
        affiliate_url = ""

    source_id = str(
        raw.get("source_id", "")
    ).strip()

    price = clean_number(
        raw.get("price_mxn"),
        minimum=0.01
    )

    commission = clean_number(
        raw.get("commission_percent"),
        minimum=0,
        maximum=100
    )

    store = str(
        raw.get("store", "")
    ).strip()

    seller = str(
        raw.get("seller", "")
    ).strip()

    # Solo se considera comprobado cuando la fuente
    # entrega el precio y existe un enlace válido.
    # Solo una fuente autorizada puede marcar datos como verificados.
    # Deben existir precio, comisión y ambos enlaces comerciales.
    verified = bool(
        source_name == "authorized_feed"
        and price != ""
        and commission != ""
        and product_url
        and affiliate_url
    )

    status = (
        "ready_for_evaluation"
        if verified
        else "incomplete"
    )

    product_id = generate_product_id(
        name,
        source_id or affiliate_url or product_url
    )

    return {
        "product_id": product_id,
        "name": name,
        "category": category,
        "store": store,
        "seller": seller,
        "price_mxn": price,
        "commission_percent": commission,
        "product_url": product_url,
        "affiliate_url": affiliate_url,
        "source": source_name,
        "source_id": source_id,
        "verified_at": (
            datetime.now(config.TIMEZONE).isoformat()
            if verified
            else ""
        ),
        "status": status,
    }


# =================================================
# LECTURA DEL CATÁLOGO
# =================================================

def load_products():
    """
    Carga los productos guardados.
    """

    initialize_catalog()

    products = []

    try:

        with open(
            PRODUCTS_FILE,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                products.append(row)

    except (OSError, csv.Error) as error:

        logger.error(
            "No se pudo leer el catálogo: %s",
            error
        )

    return products


# =================================================
# DETECCIÓN DE DUPLICADOS
# =================================================

def is_duplicate(product, existing_products):
    """
    Detecta productos existentes por ID o enlace.
    """

    for existing in existing_products:

        if (
            product["product_id"]
            == existing.get("product_id")
        ):
            return True

        new_links = {
            product.get("affiliate_url"),
            product.get("product_url"),
        }

        old_links = {
            existing.get("affiliate_url"),
            existing.get("product_url"),
        }

        new_links.discard("")
        old_links.discard("")

        if new_links.intersection(old_links):
            return True

    return False


# =================================================
# GUARDAR PRODUCTOS
# =================================================

def save_products(products):
    """
    Guarda productos nuevos sin eliminar el historial.
    """

    initialize_catalog()

    existing = load_products()

    added = 0
    skipped = 0

    for product in products:

        if not product:
            skipped += 1
            continue

        if is_duplicate(product, existing):

            skipped += 1
            continue

        existing.append(product)
        added += 1

    try:

        temporary = PRODUCTS_FILE.with_suffix(".tmp")
        with open(
            temporary,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=PRODUCT_FIELDS)
            writer.writeheader()
            writer.writerows(existing)
        temporary.replace(PRODUCTS_FILE)

        logger.info(
            "Productos agregados: %s | Duplicados o inválidos: %s",
            added,
            skipped
        )

    except (OSError, csv.Error) as error:

        logger.exception(
            "Error al guardar productos: %s",
            error
        )

        raise

    return {
        "added": added,
        "skipped": skipped,
        "total": len(existing),
    }


# =================================================
# IMPORTAR ARCHIVO JSON
# =================================================

def import_json_file(file_path):
    """
    Importa productos desde un archivo JSON local.

    El archivo puede contener una lista de productos
    o un objeto con una propiedad 'products'.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"No existe el archivo: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if isinstance(data, dict):
        data = data.get("products", [])

    if not isinstance(data, list):
        raise ValueError(
            "El JSON debe contener una lista de productos."
        )

    normalized = []

    for item in data[:MAX_PRODUCTS_PER_FEED]:

        product = normalize_product(
            item,
            source_name="manual"
        )

        if product:
            normalized.append(product)

    return save_products(normalized)


# =================================================
# CONSULTAR FUENTES AUTORIZADAS
# =================================================

def get_configured_feeds():
    """
    Lee las direcciones de fuentes autorizadas.

    Configurar PRODUCT_FEED_URLS como una lista
    separada por punto y coma.
    """

    raw = os.getenv(
        "PRODUCT_FEED_URLS",
        ""
    )

    feeds = [
        item.strip()
        for item in raw.split(";")
        if item.strip()
    ]

    return [
        url for url in feeds
        if valid_url(url)
    ]


def fetch_feed(url):
    """
    Consulta un feed JSON HTTPS configurado por el usuario.

    La fuente debe permitir expresamente su consulta.
    """

    headers = {
        "Accept": "application/json",
        "User-Agent": "FortalezaShopAI/1.0",
    }

    token = os.getenv(
        "PRODUCT_FEED_TOKEN",
        ""
    )

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            data = data.get("products", [])

        if not isinstance(data, list):
            raise ValueError(
                "La fuente no devolvió una lista de productos."
            )

        normalized = []

        for item in data[:MAX_PRODUCTS_PER_FEED]:

            product = normalize_product(
                item,
                source_name="authorized_feed"
            )

            if product:
                normalized.append(product)

        logger.info(
            "Fuente consultada. Productos válidos: %s",
            len(normalized)
        )

        return normalized

    except (
        requests.RequestException,
        ValueError,
        json.JSONDecodeError
    ) as error:

        logger.error(
            "Error consultando fuente %s: %s",
            url,
            error
        )

        return []


# =================================================
# BUSCADOR PRINCIPAL
# =================================================

def find_products():
    """
    Busca productos en todas las fuentes configuradas.
    """

    logger.info(
        "Iniciando búsqueda de productos."
    )

    feeds = get_configured_feeds()

    if not feeds:

        logger.warning(
            "No hay fuentes autorizadas configuradas."
        )

        return {
            "added": 0,
            "skipped": 0,
            "total": len(load_products()),
            "message": "Configura PRODUCT_FEED_URLS para buscar.",
        }

    discovered = []

    for feed_url in feeds:

        products = fetch_feed(feed_url)

        discovered.extend(products)

    result = save_products(discovered)

    logger.info(
        "Búsqueda finalizada: %s",
        result
    )

    return result


# =================================================
# CONSULTAR PRODUCTOS POR CATEGORÍA
# =================================================

def get_products_by_category(category):
    """
    Devuelve productos de una categoría específica.
    """

    category = str(
        category
    ).strip().lower()

    if category not in VALID_CATEGORIES:
        return []

    products = load_products()

    return [
        product
        for product in products
        if product.get("category") == category
    ]


# =================================================
# RESUMEN DEL CATÁLOGO
# =================================================

def catalog_summary():
    """
    Genera un resumen del catálogo.
    """

    products = load_products()

    summary = {
        "total": len(products),
        "complete": 0,
        "incomplete": 0,
        "categories": {},
    }

    for category in VALID_CATEGORIES:
        summary["categories"][category] = 0

    for product in products:

        if product.get("status") == "ready_for_evaluation":
            summary["complete"] += 1
        else:
            summary["incomplete"] += 1

        category = product.get("category")

        if category in summary["categories"]:
            summary["categories"][category] += 1

    return summary


# =================================================
# EJECUCIÓN DIRECTA
# =================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    print("=" * 50)
    print("FORTALEZA SHOP AI")
    print("PRODUCT FINDER")
    print("=" * 50)

    initialize_catalog()

    result = find_products()

    print("\nRESULTADO DE BÚSQUEDA")

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

    print("\nRESUMEN DEL CATÁLOGO")

    print(
        json.dumps(
            catalog_summary(),
            indent=4,
            ensure_ascii=False
        )
    )