
"""
====================================================
FORTALEZA SHOP AI
AI SCRIPT GENERATOR
Generador inteligente de guiones comerciales
====================================================

Funciones:
- Crear ganchos comerciales.
- Generar guiones para videos verticales.
- Crear escenas y narraciones.
- Generar subtítulos.
- Crear llamadas a la acción.
- Evitar repeticiones.
- Guardar historial de guiones.

Requiere OPENAI_API_KEY para generar guiones con IA.
"""

import json
import logging
import re
import hashlib

from datetime import datetime
from pathlib import Path

from openai import OpenAI

import config

from core.product_scorer import get_top_products


# ====================================================
# CONFIGURACIÓN
# ====================================================

logger = logging.getLogger(
    "FORTALEZA_SHOP_AI.SCRIPT_GENERATOR"
)

SCRIPTS_DIR = config.OUTPUT_DIR / "scripts"

SCRIPT_HISTORY_FILE = (
    config.DATA_DIR / "scripts_history.json"
)

MIN_DURATION = config.MIN_VIDEO_DURATION
MAX_DURATION = config.MAX_VIDEO_DURATION

DEFAULT_DURATION = 30

MAX_HISTORY = 500

LANGUAGE = "es-MX"


# ====================================================
# INICIALIZACIÓN
# ====================================================

def initialize_script_system():

    config.initialize_directories()

    SCRIPTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not SCRIPT_HISTORY_FILE.exists():

        with open(
            SCRIPT_HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                ensure_ascii=False,
                indent=4
            )


# ====================================================
# CLIENTE OPENAI
# ====================================================

def get_openai_client():

    if not config.OPENAI_API_KEY:

        raise RuntimeError(
            "Falta configurar OPENAI_API_KEY."
        )

    return OpenAI(
        api_key=config.OPENAI_API_KEY,
        timeout=60.0,
        max_retries=2
    )


# ====================================================
# HISTORIAL
# ====================================================

def load_script_history():

    initialize_script_system()

    try:

        with open(
            SCRIPT_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data if isinstance(data, list) else []

    except (OSError, json.JSONDecodeError) as error:

        logger.error(
            "Error leyendo historial: %s",
            error
        )

        return []


def save_script_history(history):

    initialize_script_system()

    history = history[-MAX_HISTORY:]

    temporary_file = SCRIPT_HISTORY_FILE.with_suffix(
        ".tmp"
    )

    with open(
        temporary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=4
        )

    temporary_file.replace(
        SCRIPT_HISTORY_FILE
    )


# ====================================================
# IDENTIFICADORES
# ====================================================

def generate_script_id(product_id, hook):

    raw = (
        f"{product_id}|"
        f"{hook}|"
        f"{datetime.now(config.TIMEZONE).isoformat()}"
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:16]


def normalize_text(value):

    return re.sub(
        r"\s+",
        " ",
        str(value).strip().lower()
    )


# ====================================================
# VALIDACIÓN DE PRODUCTOS
# ====================================================

def validate_product(product):

    if not isinstance(product, dict):
        return False

    required = [
        "product_id",
        "name",
        "category",
        "affiliate_url",
    ]

    for field in required:

        if not product.get(field):
            return False

    if product.get("eligible") is False:
        return False

    return True


# ====================================================
# INFORMACIÓN COMERCIAL
# ====================================================

def prepare_product_information(product):

    return {
        "name": product.get("name"),
        "category": product.get("category"),
        "store": product.get("store", ""),
        "price_mxn": product.get("price_mxn", ""),
        "commission_percent": product.get(
            "commission_percent",
            ""
        ),
        "affiliate_url": product.get(
            "affiliate_url"
        ),
    }


# ====================================================
# CONSULTAR GUIONES ANTERIORES
# ====================================================

def get_previous_hooks(limit=20):

    history = load_script_history()

    hooks = []

    for item in reversed(history):

        hook = item.get("hook", "")

        if hook:
            hooks.append(hook)

        if len(hooks) >= limit:
            break

    return hooks


def get_previous_scripts(product_id, limit=5):

    history = load_script_history()

    scripts = []

    for item in reversed(history):

        if item.get("product_id") == product_id:

            scripts.append({
                "hook": item.get("hook", ""),
                "script_id": item.get("script_id", ""),
            })

        if len(scripts) >= limit:
            break

    return scripts


# ====================================================
# CONSTRUCCIÓN DEL PROMPT
# ====================================================

def build_script_prompt(product, duration):

    information = prepare_product_information(
        product
    )

    previous_hooks = get_previous_hooks()

    previous_scripts = get_previous_scripts(
        product.get("product_id")
    )

    prompt = f"""
Eres el director creativo de FORTALEZA SHOP AI.

Tu trabajo es crear comerciales cortos para TikTok,
Instagram Reels y YouTube Shorts.

IDENTIDAD:
- Marca: FORTALEZA SHOP AI
- Mercado: México
- Idioma: Español mexicano natural.
- Estilo: Dinámico, comercial y convincente.
- Formato: Video vertical 9:16.
- Presentador: Voz en off, sin mostrar el rostro.
- Duración objetivo: {duration} segundos.

INFORMACIÓN DEL PRODUCTO:

{json.dumps(information, ensure_ascii=False, indent=2)}

REGLAS IMPORTANTES:

1. No inventes características.
2. No inventes precios ni descuentos.
3. No inventes opiniones de compradores.
4. No afirmes que un producto es el más vendido
   si no existe evidencia.
5. No prometas resultados garantizados.
6. No inventes disponibilidad.
7. No menciones comisiones al consumidor.
8. No uses afirmaciones engañosas.
9. No uses frases repetitivas.
10. No inventes especificaciones técnicas.
11. Utiliza español mexicano natural.
12. El guion debe funcionar sin mostrar una cara.
13. La llamada a la acción debe ser clara.
14. No afirmes que el producto está en oferta
    si no existe información comprobada.

ESTRUCTURA DEL VIDEO:

- Inicio: gancho fuerte de 0 a 3 segundos.
- Desarrollo: mostrar el producto y su utilidad.
- Demostración: explicar lo que realmente se conoce.
- Cierre: llamada a la acción.
- Subtítulos cortos y fáciles de leer.

DURACIÓN:
El video debe durar aproximadamente {duration} segundos.

EVITA ESTOS GANCHOS ANTERIORES:

{json.dumps(previous_hooks, ensure_ascii=False)}

OTROS GUIONES DEL MISMO PRODUCTO:

{json.dumps(previous_scripts, ensure_ascii=False)}

FORMATO DE RESPUESTA:

Devuelve exclusivamente un objeto JSON válido.

La estructura debe ser:

{{
    "title": "Título comercial",
    "hook": "Gancho inicial",
    "angle": "Enfoque creativo",
    "duration_seconds": {duration},
    "voice_style": "Descripción de la voz",
    "scenes": [
        {{
            "start": 0,
            "end": 3,
            "visual": "Descripción visual",
            "narration": "Texto de narración",
            "subtitle": "Texto en pantalla"
        }}
    ],
    "full_narration": "Narración completa",
    "call_to_action": "Llamada a la acción",
    "caption": "Descripción para redes sociales",
    "hashtags": [
        "#FortalezaShopAI"
    ]
}}

Genera entre 4 y 7 escenas.

Los tiempos deben estar ordenados y no superar
la duración solicitada.

Cada escena debe incluir una idea visual realizable
mediante imágenes o videos del producto.

No incluyas información comercial no comprobada.
"""

    return prompt


# ====================================================
# GENERACIÓN CON INTELIGENCIA ARTIFICIAL
# ====================================================

def generate_script(product, duration=DEFAULT_DURATION):

    if not validate_product(product):

        raise ValueError(
            "El producto no contiene información suficiente."
        )

    duration = int(duration)

    if not MIN_DURATION <= duration <= MAX_DURATION:

        raise ValueError(
            f"La duración debe estar entre "
            f"{MIN_DURATION} y {MAX_DURATION} segundos."
        )

    client = get_openai_client()

    prompt = build_script_prompt(
        product,
        duration
    )

    logger.info(
        "Generando guion para: %s",
        product.get("name")
    )

    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un experto en publicidad digital "
                    "y producción de videos comerciales. "
                    "Responde únicamente con JSON válido."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        },
        temperature=0.8,
        max_tokens=2500,
    )

    content = response.choices[0].message.content

    if not content:

        raise RuntimeError(
            "La IA devolvió una respuesta vacía."
        )

    try:

        script = json.loads(content)

    except json.JSONDecodeError as error:

        raise ValueError(
            "La respuesta de IA no contiene JSON válido."
        ) from error

    return script


# ====================================================
# VALIDACIÓN DEL GUION
# ====================================================

def validate_script(script, duration):

    required = [
        "title",
        "hook",
        "scenes",
        "full_narration",
        "call_to_action",
        "caption",
        "hashtags",
    ]

    for field in required:

        if not script.get(field):
            raise ValueError(
                f"Falta el campo obligatorio: {field}"
            )

    scenes = script.get("scenes")

    if not isinstance(scenes, list):
        raise ValueError(
            "Las escenas deben ser una lista."
        )

    if not 4 <= len(scenes) <= 7:

        raise ValueError(
            "El guion debe contener entre 4 y 7 escenas."
        )

    previous_end = 0

    for scene in scenes:

        for field in [
            "start",
            "end",
            "visual",
            "narration",
            "subtitle",
        ]:

            if field not in scene:
                raise ValueError(
                    f"Escena incompleta: falta {field}"
                )

        start = int(scene["start"])
        end = int(scene["end"])

        if start < previous_end:
            raise ValueError(
                "Los tiempos de las escenas se superponen."
            )

        if start < 0 or end <= start or end > duration:
            raise ValueError(
                "Los tiempos de una escena son inválidos."
            )

        previous_end = end

    return True


# ====================================================
# PREVENCIÓN DE REPETICIONES
# ====================================================

def is_repeated_hook(hook):

    normalized = normalize_text(hook)

    history = load_script_history()

    for item in history:

        previous = normalize_text(
            item.get("hook", "")
        )

        if normalized and normalized == previous:
            return True

    return False


# ====================================================
# GENERACIÓN CON REINTENTOS
# ====================================================

def generate_unique_script(
    product,
    duration=DEFAULT_DURATION,
    max_attempts=3
):

    for attempt in range(1, max_attempts + 1):

        script = generate_script(
            product,
            duration
        )

        validate_script(
            script,
            duration
        )

        if not is_repeated_hook(
            script["hook"]
        ):

            return script

        logger.warning(
            "Gancho repetido. Intento %s/%s",
            attempt,
            max_attempts
        )

    raise RuntimeError(
        "No se pudo generar un gancho nuevo."
    )


# ====================================================
# GUARDAR GUION
# ====================================================

def save_script(product, script):

    initialize_script_system()

    script_id = generate_script_id(
        product.get("product_id", ""),
        script.get("hook", "")
    )

    output = {
        "script_id": script_id,
        "product_id": product.get("product_id"),
        "product_name": product.get("name"),
        "product_category": product.get("category"),
        "affiliate_url": product.get("affiliate_url"),
        "generated_at": datetime.now(
            config.TIMEZONE
        ).isoformat(),
        "status": "generated",
        "script": script,
    }

    file_path = SCRIPTS_DIR / f"{script_id}.json"

    temporary_file = file_path.with_suffix(".tmp")

    with open(
        temporary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    temporary_file.replace(file_path)

    history = load_script_history()

    history.append({
        "script_id": script_id,
        "product_id": product.get("product_id"),
        "product_name": product.get("name"),
        "hook": script.get("hook"),
        "generated_at": output["generated_at"],
    })

    save_script_history(history)

    logger.info(
        "Guion guardado: %s",
        script_id
    )

    return output


# ====================================================
# PROCESAR UN PRODUCTO
# ====================================================

def process_product(product, duration=DEFAULT_DURATION):

    logger.info(
        "Procesando producto: %s",
        product.get("name")
    )

    script = generate_unique_script(
        product,
        duration
    )

    validate_script(
        script,
        duration
    )

    return save_script(
        product,
        script
    )


# ====================================================
# PROCESAR MEJORES PRODUCTOS
# ====================================================

def generate_scripts_for_top_products(
    limit=3,
    duration=DEFAULT_DURATION
):

    products = get_top_products(limit)

    results = []

    for product in products:

        try:

            result = process_product(
                product,
                duration
            )

            results.append({
                "success": True,
                "script_id": result["script_id"],
                "product_name": result["product_name"],
                "file": str(
                    SCRIPTS_DIR /
                    f"{result['script_id']}.json"
                ),
            })

        except Exception as error:

            logger.exception(
                "Error generando guion para %s",
                product.get("name")
            )

            results.append({
                "success": False,
                "product_name": product.get("name"),
                "error": str(error),
            })

    return results


# ====================================================
# EJECUCIÓN DIRECTA
# ====================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    print("=" * 55)
    print("FORTALEZA SHOP AI")
    print("AI SCRIPT GENERATOR")
    print("=" * 55)

    initialize_script_system()

    try:

        results = generate_scripts_for_top_products(
            limit=3,
            duration=DEFAULT_DURATION
        )

        print(
            json.dumps(
                results,
                indent=4,
                ensure_ascii=False
            )
        )

    except Exception as error:

        logger.exception(
            "No se pudieron generar los guiones: %s",
            error
        )

    print("\nProceso finalizado.")