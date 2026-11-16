
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "data" / "product_assets"
OUTPUT_DIR = ROOT / "output" / "assets"

SUPPORTED_IMAGES = {".jpg", ".jpeg", ".png", ".webp"}
SUPPORTED_VIDEOS = {".mp4", ".mov", ".webm"}


def build_asset_report(product_id):
    product_folder = ASSET_DIR / product_id
    authorization_file = product_folder / "authorization.json"

    authorization = {}

    if authorization_file.exists():
        try:
            authorization = json.loads(
                authorization_file.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            authorization = {}

    files = []

    if product_folder.exists():
        for path in sorted(product_folder.iterdir()):
            if not path.is_file() or path.name == "authorization.json":
                continue

            extension = path.suffix.lower()

            if extension in SUPPORTED_IMAGES:
                kind = "image"
            elif extension in SUPPORTED_VIDEOS:
                kind = "video"
            else:
                continue

            files.append({
                "name": path.name,
                "type": kind,
                "size_bytes": path.stat().st_size
            })

    authorized = (
        authorization.get("authorized_for_promotion") is True
        and bool(authorization.get("source"))
        and bool(authorization.get("permission_reference"))
    )

    report = {
        "product_id": product_id,
        "folder_exists": product_folder.is_dir(),
        "authorization_declared": authorized,
        "authorization_verified_independently": False,
        "total_images": sum(f["type"] == "image" for f in files),
        "total_videos": sum(f["type"] == "video" for f in files),
        "assets": files,
        "ready_to_use": authorized and len(files) > 0
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_file = OUTPUT_DIR / f"{product_id}_report.json"
    report_file.write_text(
        json.dumps(report, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    return report


if __name__ == "__main__":
    result = build_asset_report("tiktok_pestanas_bq")
    print(json.dumps(result, indent=4, ensure_ascii=False))
