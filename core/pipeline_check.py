"""Comprobaciones estructurales y de dependencias de FORTALEZA SHOP AI."""
from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REQUIRED_FILES = [
    "config.py", "main.py", "requirements.txt",
    "core/product_finder.py", "core/product_scorer.py",
    "core/script_generator.py", "core/voice_generator.py",
    "core/video_generator.py", "core/product_assets.py",
    "core/content_planner.py", "core/asset_library.py",
    "core/asset_report.py", "core/asset_organizer.py",
    "core/media_pipeline.py", "core/pipeline_check.py",
    "core/publishing_manager.py", "core/analytics.py",
    "core/system_test.py",
]
REQUIRED_FOLDERS = [
    "core", "data", "data/product_assets", "output",
    "output/videos", "output/pipeline", "output/assets",
    "output/ready_to_publish",
]
REQUIRED_PACKAGES = {"PIL": "Pillow", "moviepy": "MoviePy", "edge_tts": "edge-tts", "requests": "requests"}

def run_check(write_report=True):
    import config
    config.initialize_directories()
    files = [{"element": name, "status": "OK" if (ROOT / name).is_file() else "FALTA"} for name in REQUIRED_FILES]
    folders = [{"element": name, "status": "OK" if (ROOT / name).is_dir() else "FALTA"} for name in REQUIRED_FOLDERS]
    packages = []
    for module, label in REQUIRED_PACKAGES.items():
        try:
            installed = importlib.util.find_spec(module) is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            installed = False
        packages.append({"element": label, "status": "OK" if installed else "NO INSTALADO"})
    report = {"files": files, "folders": folders, "packages": packages}
    checks = [item for section in report.values() for item in section]
    problems = sum(item["status"] != "OK" for item in checks)
    report["summary"] = {"total_checks": len(checks), "problems": problems, "ready": problems == 0}
    if write_report:
        output = ROOT / "output" / "pipeline" / "system_check.json"
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for section, items in report.items():
        if section != "summary":
            print("\n" + section.upper())
            for item in items:
                print(f"[{item['status']}] {item['element']}")
    print(f"\nRevisiones: {len(checks)} | Problemas: {problems}")
    print("Estado: LISTO" if problems == 0 else "Estado: NECESITA CORRECCIONES")
    return report

if __name__ == "__main__":
    sys.exit(0 if run_check()["summary"]["ready"] else 1)
