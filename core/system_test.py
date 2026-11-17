"""Pruebas de importación y validación básica de módulos."""
from pathlib import Path
import importlib
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODULES = [
    "core.product_finder", "core.product_scorer", "core.script_generator",
    "core.voice_generator", "core.video_generator", "core.product_assets",
    "core.content_planner", "core.asset_library", "core.asset_report",
    "core.asset_organizer", "core.media_pipeline", "core.publishing_manager",
    "core.analytics", "core.pipeline_check",
]

def test_modules():
    results = []
    for name in MODULES:
        try:
            importlib.import_module(name)
            results.append({"module": name, "status": "OK"})
        except Exception as exc:
            results.append({"module": name, "status": "ERROR", "detail": f"{type(exc).__name__}: {exc}"})
    return results

def main():
    results = test_modules()
    passed = sum(item["status"] == "OK" for item in results)
    failed = len(results) - passed
    report = {"project": "FORTALEZA SHOP AI", "modules_tested": len(results), "passed": passed, "failed": failed, "results": results}
    output = ROOT / "output" / "pipeline"
    output.mkdir(parents=True, exist_ok=True)
    (output / "module_test.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in results:
        print(f"[{item['status']}] {item['module']}")
        if "detail" in item:
            print("  " + item["detail"])
    print(f"\nCorrectos: {passed} | Con problemas: {failed}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
