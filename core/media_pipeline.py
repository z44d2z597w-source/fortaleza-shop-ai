"""
Pipeline de preparación de contenido.
Genera un guion local y le asigna solo recursos con autorización declarada.
No publica contenido.
"""
import json
import re
from pathlib import Path
from core.script_generator import generate_script
from core.asset_library import scan_product_assets

BASE_DIR = Path(__file__).resolve().parent.parent

def _safe_id(value):
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "_", str(value)).strip("_")
    if not cleaned:
        raise ValueError("Identificador de producto no válido.")
    return cleaned[:80]

def prepare_product_content(product):
    if not isinstance(product, dict):
        raise ValueError("Los datos del producto no son válidos.")
    product_id = _safe_id(product.get("product_id") or product.get("id") or "")
    script = generate_script(product)
    manifest = scan_product_assets(product_id)
    usable_images = [a for a in manifest["assets"] if a["type"] == "image" and a["usable"]]
    usable_videos = [a for a in manifest["assets"] if a["type"] == "video" and a["usable"]]
    for index, scene in enumerate(script["scenes"]):
        scene["image_path"] = usable_images[index % len(usable_images)]["path"] if usable_images else None
    script["product_id"] = product_id
    script["asset_summary"] = {
        "images_available": len(usable_images),
        "videos_available": len(usable_videos),
        "authorized_materials": len(usable_images) + len(usable_videos),
    }
    script["ready_for_video"] = bool(usable_images)
    script["ready_for_publication"] = False
    script["requires_review"] = True
    output_dir = BASE_DIR / "output" / "scripts"
    output_dir.mkdir(parents=True, exist_ok=True)
    script_path = output_dir / f"{product_id}_script.json"
    temp = script_path.with_suffix(".tmp")
    temp.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(script_path)
    report = {
        "product_id": product_id,
        "script_created": True,
        "script_path": str(script_path.relative_to(BASE_DIR)),
        "authorized_images": len(usable_images),
        "authorized_videos": len(usable_videos),
        "ready_for_video": script["ready_for_video"],
        "ready_for_publication": False,
        "next_action": "Enviar al generador de video." if script["ready_for_video"] else "Agregar recursos con permiso documentado.",
    }
    report_dir = BASE_DIR / "output" / "pipeline"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"{product_id}_report.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report

if __name__ == "__main__":
    print("Pipeline listo. Llama prepare_product_content(product) desde el flujo principal.")
