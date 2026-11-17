"""Punto de entrada de FORTALEZA SHOP AI."""
import argparse
import json
import logging
import sys
from datetime import datetime

import config

def setup_logging():
    config.initialize_directories()
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

logger = logging.getLogger("FORTALEZA_SHOP_AI")

def show_banner():
    print("\n" + "=" * 54)
    print("              FORTALEZA SHOP AI")
    print("       Sistema de contenido para afiliados")
    print("=" * 54)
    print(f" Mercado: México | Idioma: {config.LANGUAGE}")
    print(f" Formato: {config.VIDEO_FORMAT} | Modo: {config.PUBLISH_MODE}")
    print(" Publicación automática: DESACTIVADA")
    print("=" * 54)

def system_status():
    status = config.get_system_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return status

def project_information():
    data = {
        "project": config.PROJECT_NAME,
        "repository": config.REPOSITORY_NAME,
        "country": config.COUNTRY,
        "language": config.LANGUAGE,
        "timezone": config.TIMEZONE_NAME,
        "mode": config.PUBLISH_MODE,
        "categories": config.PRODUCT_CATEGORIES,
        "video": config.VIDEO_SETTINGS,
        "paid_ai_enabled": config.ENABLE_PAID_AI,
        "automatic_publication": False,
        "generated_at": datetime.now(config.TIMEZONE).isoformat(),
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return data

def prepare_system():
    config.initialize_directories()
    from core.pipeline_check import run_check
    report = run_check()
    return report["summary"]["ready"]

def run_product_finder():
    from core.product_finder import find_products, catalog_summary
    result = find_products()
    print(json.dumps({"search": result, "catalog": catalog_summary()}, ensure_ascii=False, indent=2))
    return result

def run_product_scoring():
    from core.product_scorer import evaluate_catalog, save_scores, get_scoring_summary
    results = evaluate_catalog()
    save_scores(results)
    summary = get_scoring_summary(results)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary

def run_script_generator():
    from core.script_generator import generate_scripts_for_top_products
    results = generate_scripts_for_top_products(limit=3)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if not results:
        print("No hay productos elegibles. Primero importa productos con precio, comisión y enlaces verificados.")
    return results

def run_analytics():
    from core.analytics import show_report
    return show_report()

def run_prepare_content(product_id):
    from core.product_assets import load_product
    from core.media_pipeline import prepare_product_content
    product = load_product(product_id)
    result = prepare_product_content(product)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

def run_menu():
    options = {
        "1": ("Estado del sistema", system_status),
        "2": ("Buscar productos desde fuentes configuradas", run_product_finder),
        "3": ("Evaluar productos del catálogo", run_product_scoring),
        "4": ("Generar guiones gratuitos", run_script_generator),
        "5": ("Consultar estadísticas", run_analytics),
        "6": ("Información del proyecto", project_information),
    }
    while True:
        print("\n" + "-" * 45)
        for key, (label, _) in options.items():
            print(f"{key}. {label}")
        print("7. Preparar contenido de un producto")
        print("8. Salir")
        choice = input("Elige una opción: ").strip()
        if choice in options:
            try:
                options[choice][1]()
            except Exception as exc:
                logger.exception("La operación falló")
                print(f"No se pudo completar: {exc}")
        elif choice == "7":
            product_id = input("ID del producto registrado: ").strip()
            try:
                run_prepare_content(product_id)
            except Exception as exc:
                logger.exception("No se pudo preparar el contenido")
                print(f"No se pudo completar: {exc}")
        elif choice == "8":
            print("FORTALEZA SHOP AI finalizado.")
            return
        else:
            print("Opción no válida.")

def main(argv=None):
    parser = argparse.ArgumentParser(description="FORTALEZA SHOP AI")
    parser.add_argument("--check", action="store_true", help="Revisar estructura y dependencias")
    parser.add_argument("--status", action="store_true", help="Mostrar estado")
    parser.add_argument("--info", action="store_true", help="Mostrar información")
    parser.add_argument("--menu", action="store_true", help="Abrir menú")
    parser.add_argument("--find-products", action="store_true", help="Consultar feeds autorizados configurados")
    parser.add_argument("--score-products", action="store_true", help="Evaluar el catálogo")
    parser.add_argument("--generate-scripts", action="store_true", help="Generar guiones con el modo gratuito")
    parser.add_argument("--analytics", action="store_true", help="Mostrar estadísticas")
    parser.add_argument("--prepare-content", metavar="PRODUCT_ID", help="Preparar guion y revisar recursos autorizados")
    args = parser.parse_args(argv)

    setup_logging()
    show_banner()

    try:
        if args.check:
            return 0 if prepare_system() else 1
        if args.status:
            system_status()
        elif args.info:
            project_information()
        elif args.find_products:
            run_product_finder()
        elif args.score_products:
            run_product_scoring()
        elif args.generate_scripts:
            run_script_generator()
        elif args.analytics:
            run_analytics()
        elif args.prepare_content:
            run_prepare_content(args.prepare_content)
        elif args.menu:
            run_menu()
        else:
            parser.print_help()
        return 0
    except KeyboardInterrupt:
        print("\nOperación cancelada.")
        return 130
    except Exception as exc:
        logger.exception("Error de ejecución")
        print(f"Error: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
