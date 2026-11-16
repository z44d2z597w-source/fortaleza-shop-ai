
import json
from pathlib import Path

from core.script_generator import generate_script
from core.asset_library import scan_product_assets


BASE_DIR = Path(__file__).resolve().parent.parent


def prepare_product_content(product):
    """Prepara el guion y asigna imágenes autorizadas."""

    if not isinstance(product, dict):
        raise ValueError("Los datos del producto no son válidos.")

    product_id = str(
        product.get("product_id") or product.get("id") or ""
    ).strip()

    if not product_id:
        raise ValueError("El producto necesita un identificador.")

    # 1. Generar guion gratuito.
    script = generate_script(product)

    # 2. Buscar materiales locales.
    manifest = scan_product_assets(product_id)

    usable_images = [
        asset for asset in manifest["assets"]
        if asset["type"] == "image" and asset["usable"]
    ]

    usable_videos = [
        asset for asset in manifest["assets"]
        if asset["type"] == "video" and asset["usable"]
    ]

    # 3. Asignar imágenes a las escenas.
    for index, scene in enumerate(script["scenes"]):
        if usable_images:
            asset = usable_images[index % len(usable_images)]
            scene["image_path"] = asset["path"]
        else:
            scene["image_path"] = None

    # 4. Actualizar estado real del contenido.
    script["asset_summary"] = {
        "images_available": len(usable_images),
        "videos_available": len(usable_videos),
        "authorized_materials": len(usable_images) + len(usable_videos)
    }

    script["ready_for_video"] = len(usable_images) > 0
    script["ready_for_publication"] = False
    script["requires_review"] = True

    # 5. Guardar el guion actualizado.
    output_file = BASE_DIR / script["file"]

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(script, file, ensure_ascii=False, indent=4)

    # 6. Crear informe del proceso.
    report = {
        "product_id": product_id,
        "script_created": True,
        "authorized_images": len(usable_images),
        "authorized_videos": len(usable_videos),
        "ready_for_video": script["ready_for_video"],
        "ready_for_publication": False,
        "next_action": (
            "Enviar al generador de video."
            if script["ready_for_video"]
            else "Conseguir imágenes autorizadas del producto."
        )
    }

    report_dir = BASE_DIR / "output" / "pipeline"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / f"{product_id}_report.json"

    with open(report_file, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    return report


if __name__ == "__main__":
    example_product = {
        "product_id": "tiktok_pestanas_bq",
        "name": "Kit de extensiones de pestañas B&Q 30D+40D",
        "price": "$210",
        "affiliate_link": (
            "https://vt.tiktok.com/ZS9f3kHks2txK-BbsOD/"
        )
    }

    result = prepare_product_content(example_product)

    print(json.dumps(result, ensure_ascii=False, indent=4))