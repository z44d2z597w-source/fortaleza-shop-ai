
"""
==========================================
FORTALEZA SHOP AI
CENTRO DE CONTROL PRINCIPAL
==========================================
"""

import argparse
import json
import logging
import sys

from datetime import datetime
from pathlib import Path

import config


# ==========================================
# INICIALIZACIÓN
# ==========================================

config.initialize_directories()

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            config.LOG_FILE,
            encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("FORTALEZA_SHOP_AI")


# ==========================================
# PRESENTACIÓN
# ==========================================

def show_banner():

    print("\n")
    print("=" * 55)
    print("       FORTALEZA SHOP AI")
    print("       AUTOMATIZACIÓN COMERCIAL")
    print("=" * 55)
    print(" Mercado: México")
    print(" Idioma: Español")
    print(" Formato: Video vertical 9:16")
    print(f" Modo: {config.PUBLISH_MODE}")
    print("=" * 55)


# ==========================================
# ESTADO DEL SISTEMA
# ==========================================

def system_status():

    status = config.get_system_status()

    print("\nESTADO DEL SISTEMA")
    print("-" * 45)

    for name, value in status.items():
        print(f"{name}: {value}")

    print("-" * 45)

    return status


# ==========================================
# VERIFICACIÓN DE ARCHIVOS
# ==========================================

def check_project():

    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
    ]

    print("\nVERIFICACIÓN DEL PROYECTO")

    errors = []

    for filename in required_files:

        file_path = config.BASE_DIR / filename

        if file_path.exists():
            print(f"[OK] {filename}")
        else:
            print(f"[FALTA] {filename}")
            errors.append(filename)

    return errors


# ==========================================
# INFORMACIÓN DEL PROYECTO
# ==========================================

def project_information():

    information = {
        "project": config.PROJECT_NAME,
        "repository": config.REPOSITORY_NAME,
        "country": config.COUNTRY,
        "language": config.LANGUAGE,
        "timezone": "America/Mexico_City",
        "mode": config.PUBLISH_MODE,
        "categories": config.PRODUCT_CATEGORIES,
        "video": config.VIDEO_SETTINGS,
        "rules": config.RULES,
        "generated_at": datetime.now(
            config.TIMEZONE
        ).isoformat(),
    }

    print(
        json.dumps(
            information,
            indent=4,
            ensure_ascii=False,
            default=str
        )
    )

    return information


# ==========================================
# PREPARACIÓN DEL SISTEMA
# ==========================================

def prepare_system():

    logger.info("Iniciando preparación del sistema.")

    config.initialize_directories()

    errors = check_project()

    if errors:
        logger.error(
            "Faltan archivos obligatorios: %s",
            ", ".join(errors)
        )
        return False

    logger.info("Carpetas verificadas correctamente.")

    system_status()

    logger.info(
        "FORTALEZA SHOP AI está preparado."
    )

    return True


# ==========================================
# EJECUCIÓN DE MÓDULOS
# ==========================================

def run_product_finder():

    logger.info(
        "El buscador de productos todavía está en construcción."
    )

    print(
        "\nPRODUCT FINDER: pendiente de implementación."
    )


def run_script_generator():

    logger.info(
        "El generador de guiones todavía está en construcción."
    )

    print(
        "\nAI SCRIPT: pendiente de implementación."
    )


def run_video_generator():

    logger.info(
        "El generador de videos todavía está en construcción."
    )

    print(
        "\nVIDEO MAKER: pendiente de implementación."
    )


def run_analytics():

    logger.info(
        "El módulo de estadísticas todavía está en construcción."
    )

    print(
        "\nANALYTICS: pendiente de implementación."
    )


# ==========================================
# MENÚ DE OPERACIONES
# ==========================================

def run_menu():

    while True:

        print("\n")
        print("=" * 45)
        print("       FORTALEZA SHOP AI")
        print("=" * 45)

        print("1. Estado del sistema")
        print("2. Buscar productos")
        print("3. Generar guiones")
        print("4. Crear videos")
        print("5. Consultar estadísticas")
        print("6. Información del proyecto")
        print("7. Salir")

        option = input(
            "\nSelecciona una opción: "
        ).strip()

        if option == "1":

            system_status()

        elif option == "2":

            run_product_finder()

        elif option == "3":

            run_script_generator()

        elif option == "4":

            run_video_generator()

        elif option == "5":

            run_analytics()

        elif option == "6":

            project_information()

        elif option == "7":

            print(
                "\nFORTALEZA SHOP AI finalizado."
            )

            break

        else:

            print(
                "\nOpción no válida."
            )


# ==========================================
# ARGUMENTOS DE EJECUCIÓN
# ==========================================

def main():

    parser = argparse.ArgumentParser(
        description="FORTALEZA SHOP AI"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Verificar el sistema"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Mostrar estado"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar información"
    )

    parser.add_argument(
        "--menu",
        action="store_true",
        help="Abrir menú interactivo"
    )

    args = parser.parse_args()

    show_banner()

    if args.check:

        success = prepare_system()

        sys.exit(
            0 if success else 1
        )

    elif args.status:

        system_status()

    elif args.info:

        project_information()

    elif args.menu:

        prepare_system()
        run_menu()

    else:

        prepare_system()

        print(
            "\nUtiliza --help para consultar las opciones."
        )


# ==========================================
# INICIO
# ==========================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\nEjecución interrumpida por el usuario."
        )

        sys.exit(130)

    except Exception as error:

        logger.exception(
            "Error crítico: %s",
            error
        )

        sys.exit(1)
