
"""
FORTALEZA SHOP AI
Administrador de productos y material promocional.

Guarda los datos de productos y organiza imágenes y videos
autorizados para su utilización en contenido de afiliados.

No realiza scraping ni evade restricciones de TikTok.
"""

import json
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
import config


logger = logging.getLogger("FORTALEZA_SHOP_AI.product_assets")

DATA_DIR = Path(config.DATA_DIR) / "products"
ASSETS_DIR = Path(config.DATA_DIR) / "product_assets"

MAX_IMAGE_SIZE = 20 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024

MIME_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
}


def safe_name(value):
    """Genera nombres de archivos seguros."""
    value = re.sub(
        r"[^\w\-]+",
        "_",
        str(value),
        flags=re.UNICODE,
    )
    return value.strip("_")[:70] or "producto"


def initialize_directories():
    """Prepara las carpetas del administrador."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def product_file(product_id):
    """Obtiene la ubicación del registro del producto."""
    return DATA_DIR / f"{safe_name(product_id)}.json"


def product_asset_folder(product_id):
    """Obtiene la carpeta de recursos del producto."""
    folder = ASSETS_DIR / safe_name(product_id)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_product(product):
    """Guarda un producto en formato JSON."""
    initialize_directories()

    product_id = safe_name(product.get("id", ""))

    if not product_id:
        raise ValueError("El producto necesita un identificador.")

    product["id"] = product_id

    destination = product_file(product_id)

    with destination.open("w", encoding="utf-8") as file:
        json.dump(
            product,
            file,
            ensure_ascii=False,
            indent=4,
        )

    product_asset_folder(product_id)

    logger.info("Producto guardado: %s", product_id)

    return str(destination)


def load_product(product_id):
    """Carga un producto guardado."""
    path = product_file(product_id)

    if not path.exists():
        raise FileNotFoundError(
            f"No existe el producto: {product_id}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def register_product(
    product_id,
    name,
    affiliate_url,
    price=None,
    commission=None,
    commission_rate=None,
    stock=None,
    platform="TikTok Shop",
):
    """Registra un producto para futuras promociones."""

    parsed = urlparse(affiliate_url)

    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("El enlace debe utilizar HTTPS.")

    product = {
        "id": safe_name(product_id),
        "name": name,
        "platform": platform,
        "affiliate_url": affiliate_url,
        "price_mxn": price,
        "estimated_commission_mxn": commission,
        "commission_rate_percent": commission_rate,
        "observed_stock": stock,
        "currency": "MXN",
        "assets": [],
        "status": "registered",
        "asset_usage_note": (
            "Utilizar únicamente material promocional "
            "autorizado por el vendedor o la plataforma."
        ),
    }

    return save_product(product)


def register_initial_product():
    """
    Registra el primer producto candidato de FORTALEZA SHOP AI.
    Los datos comerciales son los observados al registrarlo
    y pueden cambiar en TikTok Shop.
    """

    return register_product(
        product_id="tiktok_pestanas_bq",
        name="Kit de extensiones de pestañas B&Q 30D+40D",
        affiliate_url=(
            "https://vt.tiktok.com/ZS9f3kHks2txK-BbsOD/"
        ),
        price=125.00,
        commission=16.80,
        commission_rate=8,
        stock=6213,
    )


def download_authorized_asset(
    product_id,
    asset_url,
    asset_type="image",
):
    """
    Descarga una imagen o video desde una URL directa
    proporcionada por una fuente autorizada.

    No descarga páginas HTML ni enlaces cortos de producto.
    No sigue redirecciones.
    """

    parsed = urlparse(asset_url)

    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("El recurso debe tener una URL HTTPS.")

    if asset_type not in ("image", "video"):
        raise ValueError("Tipo permitido: image o video.")

    product = load_product(product_id)

    max_size = (
        MAX_IMAGE_SIZE
        if asset_type == "image"
        else MAX_VIDEO_SIZE
    )

    response = requests.get(
        asset_url,
        stream=True,
        timeout=25,
        allow_redirects=False,
        headers={
            "User-Agent": "FORTALEZA-SHOP-AI/1.0"
        },
    )

    try:
        response.raise_for_status()

        content_type = (
            response.headers.get("Content-Type", "")
            .split(";")[0]
            .strip()
            .lower()
        )

        expected_prefix = (
            "image/"
            if asset_type == "image"
            else "video/"
        )

        extension = MIME_EXTENSIONS.get(content_type)

        if not content_type.startswith(expected_prefix):
            raise ValueError(
                "La dirección no contiene un recurso "
                "multimedia del tipo solicitado."
            )

        if not extension:
            raise ValueError(
                f"Formato no admitido: {content_type}"
            )

        content_length = int(
            response.headers.get("Content-Length", 0)
        )

        if content_length > max_size:
            raise ValueError("El archivo supera el límite permitido.")

        folder = product_asset_folder(product_id)

        number = len(product.get("assets", [])) + 1

        destination = folder / (
            f"{safe_name(product_id)}_{number}{extension}"
        )

        temporary = destination.with_suffix(
            destination.suffix + ".tmp"
        )

        total = 0

        try:
            with temporary.open("wb") as file:
                for chunk in response.iter_content(64 * 1024):
                    if not chunk:
                        continue

                    total += len(chunk)

                    if total > max_size:
                        raise ValueError(
                            "El archivo supera el límite permitido."
                        )

                    file.write(chunk)

            temporary.replace(destination)

        except Exception:
            temporary.unlink(missing_ok=True)
            raise

        product.setdefault("assets", []).append({
            "type": asset_type,
            "path": str(destination),
            "source": asset_url,
            "content_type": content_type,
            "authorized_source_confirmed": False,
        })

        save_product(product)

        return {
            "success": True,
            "path": str(destination),
            "size_bytes": total,
            "type": asset_type,
        }

    finally:
        response.close()


def get_product_assets(product_id):
    """Devuelve los recursos registrados del producto."""
    product = load_product(product_id)
    return product.get("assets", [])


def get_product_summary():
    """Genera un resumen de los productos registrados."""
    initialize_directories()

    products = []

    for path in DATA_DIR.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as file:
                product = json.load(file)

            products.append({
                "id": product.get("id"),
                "name": product.get("name"),
                "platform": product.get("platform"),
                "assets": len(product.get("assets", [])),
                "status": product.get("status"),
            })

        except (OSError, json.JSONDecodeError):
            logger.warning(
                "No se pudo leer el registro: %s",
                path,
            )

    return {
        "total_products": len(products),
        "products": products,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    saved_path = register_initial_product()

    print("Primer producto registrado:")
    print(saved_path)

    print(
        json.dumps(
            get_product_summary(),
            indent=4,
            ensure_ascii=False,
        )
    )