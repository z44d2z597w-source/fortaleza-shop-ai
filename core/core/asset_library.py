
import json
import hashlib
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "data" / "product_assets"
MANIFEST_DIR = BASE_DIR / "output" / "assets"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm"}

ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def safe_id(value):
    """Evita nombres de carpeta inseguros."""
    value = str(value).strip().lower()

    cleaned = "".join(
        char if char.isalnum() or char in "-_" else "_"
        for char in value
    )

    cleaned = cleaned.strip("_")

    if not cleaned:
        raise ValueError("El producto necesita un ID válido.")

    return cleaned


def file_hash(path):
    """Calcula una huella para identificar cada archivo."""
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def load_authorization(product_folder):
    """
    Lee la autorización declarada manualmente.

    No comprueba por sí mismo los derechos de uso.
    La autorización debe provenir del vendedor o plataforma.
    """
    authorization_file = product_folder / "authorization.json"

    if not authorization_file.exists():
        return {
            "authorized_for_promotion": False,
            "source": "",
            "permission_reference": ""
        }

    try:
        with open(authorization_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Formato de autorización incorrecto.")

        authorized = (
            data.get("authorized_for_promotion") is True
            and bool(str(data.get("source", "")).strip())
            and bool(str(data.get("permission_reference", "")).strip())
        )

        return {
            "authorized_for_promotion": authorized,
            "source": str(data.get("source", "")).strip(),
            "permission_reference": str(
                data.get("permission_reference", "")
            ).strip()
        }

    except (OSError, json.JSONDecodeError, ValueError):
        return {
            "authorized_for_promotion": False,
            "source": "",
            "permission_reference": ""
        }


def scan_product_assets(product_id):
    """
    Organiza las imágenes y videos locales de un producto.
    No descarga contenido de internet ni extrae material protegido.
    """

    product_id = safe_id(product_id)

    product_folder = ASSETS_DIR / product_id
    product_folder.mkdir(parents=True, exist_ok=True)

    authorization = load_authorization(product_folder)

    assets = []

    for path in sorted(product_folder.iterdir()):
        if not path.is_file():
            continue

        if path.name == "authorization.json":
            continue

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        if path.stat().st_size == 0:
            continue

        asset_type = (
            "image"
            if path.suffix.lower() in IMAGE_EXTENSIONS
            else "video"
        )

        assets.append({
            "name": path.name,
            "path": str(path.relative_to(BASE_DIR)),
            "type": asset_type,
            "extension": path.suffix.lower(),
            "size_bytes": path.stat().st_size,
            "sha256": file_hash(path),
            "authorized_for_promotion": (
                authorization["authorized_for_promotion"]
            ),
            "usable": authorization["authorized_for_promotion"]
        })

    manifest = {
        "product_id": product_id,
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "authorization": authorization,
        "total_assets": len(assets),
        "total_images": sum(
            item["type"] == "image" for item in assets
        ),
        "total_videos": sum(
            item["type"] == "video" for item in assets
        ),
        "usable_assets": sum(
            item["usable"] for item in assets
        ),
        "assets": assets
    }

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    manifest_path = MANIFEST_DIR / f"{product_id}_manifest.json"

    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, ensure_ascii=False, indent=4)

    return manifest


def get_usable_assets(product_id):
    """Devuelve únicamente materiales con autorización declarada."""

    manifest = scan_product_assets(product_id)

    return [
        asset
        for asset in manifest["assets"]
        if asset["usable"]
    ]


if __name__ == "__main__":
    product_id = "tiktok_pestanas_bq"

    result = scan_product_assets(product_id)

    print("Revisión de materiales terminada.")
    print("Producto:", result["product_id"])
    print("Imágenes:", result["total_images"])
    print("Videos:", result["total_videos"])
    print("Materiales utilizables:", result["usable_assets"])

    if result["usable_assets"] == 0:
        print(
            "Faltan materiales autorizados. "
            "No se generará un anuncio con imágenes sin verificar."
        )
