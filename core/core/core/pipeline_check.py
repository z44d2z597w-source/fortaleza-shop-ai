
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "config.py",
    "main.py",
    "requirements.txt",
    "core/product_finder.py",
    "core/product_scorer.py",
    "core/script_generator.py",
    "core/voice_generator.py",
    "core/video_generator.py",
    "core/product_assets.py",
    "core/content_planner.py",
    "core/asset_library.py",
    "core/asset_report.py",
    "core/asset_organizer.py",
    "core/media_pipeline.py",
    "core/pipeline_check.py",
    "core/publishing_manager.py",
    "core/analytics.py",
]

REQUIRED_FOLDERS = [
    "core",
    "data",
    "data/product_assets",
    "data/product_assets/tiktok_pestanas_bq",
    "output",
    "output/videos",
    "output/pipeline",
    "output/assets",
    "output/ready_to_publish",
]

REQUIRED_PACKAGES = [
    "PIL",
    "moviepy",
    "edge_tts",
]


def check_files():
    return [
        {
            "element": name,
            "status": "OK" if (ROOT / name).is_file() else "FALTA"
        }
        for name in REQUIRED_FILES
    ]


def check_folders():
    return [
        {
            "element": name,
            "status": "OK" if (ROOT / name).is_dir() else "FALTA"
        }
        for name in REQUIRED_FOLDERS
    ]


def check_packages():
    results = []

    for package in REQUIRED_PACKAGES:
        try:
            installed = (
                importlib.util.find_spec(package) is not None
            )
        except (ImportError, ModuleNotFoundError, ValueError):
            installed = False

        results.append({
            "element": package,
            "status": "OK" if installed else "NO INSTALADO"
        })

    return results


def run_check():
    report = {
        "files": check_files(),
        "folders": check_folders(),
        "packages": check_packages(),
    }

    checks = [
        item
        for section in report.values()
        for item in section
    ]

    total = len(checks)
    problems = sum(
        item["status"] != "OK"
        for item in checks
    )

    report["summary"] = {
        "total_checks": total,
        "problems": problems,
        "ready": problems == 0
    }

    output_dir = ROOT / "output" / "pipeline"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "system_check.json"

    report_path.write_text(
        json.dumps(report, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nFORTALEZA SHOP AI")
    print("REVISION GENERAL DEL SISTEMA\n")

    for section, items in report.items():
        if section == "summary":
            continue

        print(f"\n{section.upper()}")

        for item in items:
            print(
                f"[{item['status']}] "
                f"{item['element']}"
            )

    print("\nRESUMEN")
    print(f"Total de revisiones: {total}")
    print(f"Problemas encontrados: {problems}")

    if problems == 0:
        print("Estado: LISTO")
    else:
        print("Estado: NECESITA CORRECCIONES")

    print(f"Reporte guardado en: {report_path}")


if __name__ == "__main__":
    run_check()
