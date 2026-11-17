
from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent.parent

MODULES = [
    "product_finder",
    "product_scorer",
    "script_generator",
    "voice_generator",
    "video_generator",
    "product_assets",
    "content_planner",
    "asset_library",
    "asset_report",
    "asset_organizer",
    "media_pipeline",
    "publishing_manager",
    "analytics",
    "pipeline_check",
]


def test_modules():
    results = []

    for name in MODULES:
        path = ROOT / "core" / f"{name}.py"

        if not path.is_file():
            results.append({
                "module": name,
                "status": "MISSING"
            })
            continue

        try:
            spec = importlib.util.spec_from_file_location(
                f"fortaleza_test_{name}", path
            )

            if spec is None or spec.loader is None:
                raise ImportError("No se pudo cargar el módulo.")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            results.append({
                "module": name,
                "status": "OK"
            })

        except Exception as error:
            results.append({
                "module": name,
                "status": "ERROR",
                "detail": str(error)
            })

    return results


def main():
    results = test_modules()

    passed = sum(item["status"] == "OK" for item in results)
    failed = len(results) - passed

    report = {
        "project": "FORTALEZA SHOP AI",
        "modules_tested": len(results),
        "passed": passed,
        "failed": failed,
        "results": results
    }

    output = ROOT / "output" / "pipeline"
    output.mkdir(parents=True, exist_ok=True)

    (output / "module_test.json").write_text(
        json.dumps(report, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nFORTALEZA SHOP AI - PRUEBA DE MODULOS\n")

    for item in results:
        print(f"[{item['status']}] {item['module']}")
        if "detail" in item:
            print(f"  Error: {item['detail']}")

    print(f"\nCorrectos: {passed}")
    print(f"Con problemas: {failed}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
