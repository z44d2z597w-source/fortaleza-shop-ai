
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "data" / "product_assets"

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp",
    ".mp4", ".mov", ".webm"
}


def safe_product_id(product_id):
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", product_id)

    if not cleaned:
        raise ValueError("Identificador de producto no válido.")

    return cleaned


def create_product_folder(product_id):
    product_id = safe_product_id(product_id)
    folder = ASSET_DIR / product_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def organize_asset(source_path, product_id):
    source = Path(source_path).expanduser().resolve()
    destination_folder = create_product_folder(product_id)

    if not source.is_file():
        raise FileNotFoundError("No se encontró el archivo de origen.")

    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Formato de archivo no compatible.")

    destination = destination_folder / source.name

    if destination.exists():
        raise FileExistsError(
            "Ya existe un archivo con ese nombre en la carpeta del producto."
        )

    shutil.copy2(source, destination)

    return {
        "product_id": safe_product_id(product_id),
        "file": destination.name,
        "destination": str(destination),
        "copied": True
    }


if __name__ == "__main__":
    folder = create_product_folder("tiktok_pestanas_bq")
    print("Carpeta del producto preparada:", folder)
    print("Para organizar recursos, utiliza organize_asset().")