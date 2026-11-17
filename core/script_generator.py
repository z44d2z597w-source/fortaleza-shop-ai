"""
FORTALEZA SHOP AI — generador de guiones.
Por defecto genera guiones sin coste mediante plantillas verificables.
La IA externa solo se usa si ENABLE_PAID_AI=true y OPENAI_API_KEY está configurada.
"""
import hashlib
import json
import logging
import re
from datetime import datetime
from pathlib import Path

import config
from core.product_scorer import get_top_products

logger = logging.getLogger("FORTALEZA_SHOP_AI.script_generator")
SCRIPTS_DIR = config.OUTPUT_DIR / "scripts"
SCRIPT_HISTORY_FILE = config.DATA_DIR / "scripts_history.json"
MIN_DURATION = config.MIN_VIDEO_DURATION
MAX_DURATION = config.MAX_VIDEO_DURATION
DEFAULT_DURATION = 30
MAX_HISTORY = 500

def initialize_script_system():
    config.initialize_directories()
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    if not SCRIPT_HISTORY_FILE.exists():
        SCRIPT_HISTORY_FILE.write_text("[]", encoding="utf-8")

def load_script_history():
    initialize_script_system()
    try:
        data = json.loads(SCRIPT_HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        logger.warning("Historial dañado o inaccesible; se inicia vacío.")
        return []

def save_script_history(history):
    initialize_script_system()
    temp = SCRIPT_HISTORY_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(history[-MAX_HISTORY:], ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(SCRIPT_HISTORY_FILE)

def normalize_text(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())

def validate_product(product):
    if not isinstance(product, dict):
        return False
    product_id = product.get("product_id") or product.get("id")
    name = product.get("name") or product.get("product_name")
    return bool(str(product_id or "").strip() and str(name or "").strip())

def _product_id(product):
    return str(product.get("product_id") or product.get("id") or "producto")

def _product_name(product):
    return str(product.get("name") or product.get("product_name") or "este producto").strip()

def build_script_prompt(product, duration):
    info = {
        "name": _product_name(product),
        "category": product.get("category"),
        "description": product.get("description"),
        "verified_features": product.get("features"),
        "price_mxn": product.get("price_mxn", product.get("price")),
    }
    return (
        "Crea un guion de video vertical en español mexicano. "
        "No inventes características, resultados, precios, reseñas ni descuentos. "
        f"Duración {duration} segundos. Datos disponibles: "
        + json.dumps(info, ensure_ascii=False)
        + ". Devuelve JSON con title, hook, scenes, full_narration, call_to_action, caption, hashtags."
    )

def _offline_script(product, duration):
    name = _product_name(product)
    description = str(product.get("description") or "").strip()
    features = product.get("features") or []
    if isinstance(features, str):
        features = [features]
    facts = [str(x).strip() for x in features if str(x).strip()][:3]
    known_detail = description or (", ".join(facts) if facts else "")
    intro = f"Hoy te mostramos: {name}."
    detail = known_detail if known_detail else "Revisa las características, medidas y detalles directamente en la ficha del vendedor."
    scenes = [
        {"start": 0, "end": 4, "visual": f"Primer plano del producto: {name}.", "narration": f"¿Buscas conocer {name}? Échale un vistazo.", "subtitle": f"Conoce {name}"},
        {"start": 4, "end": 10, "visual": "Mostrar el producto desde varios ángulos.", "narration": intro, "subtitle": name[:70]},
        {"start": 10, "end": 18, "visual": "Mostrar únicamente detalles visibles y comprobables.", "narration": detail, "subtitle": "Mira sus detalles"},
        {"start": 18, "end": 25, "visual": "Enseñar el contenido o presentación real del producto.", "narration": "Compara la información y confirma que sea lo que necesitas.", "subtitle": "Revisa antes de comprar"},
        {"start": 25, "end": duration, "visual": "Cierre con el producto y una llamada a la acción.", "narration": "Consulta el precio y la disponibilidad actualizados en el enlace.", "subtitle": "Consulta el enlace"},
    ]
    # Divide cualquier duración válida en cinco escenas positivas y continuas.
    points = [round(duration * index / 5) for index in range(6)]
    for index, scene in enumerate(scenes):
        scene["start"], scene["end"] = points[index], points[index + 1]
    full = " ".join(scene["narration"] for scene in scenes)
    return {
        "title": f"{name} | Conócelo antes de comprar",
        "hook": f"¿Ya conoces {name}?",
        "angle": "Presentación clara basada en información disponible",
        "duration_seconds": duration,
        "voice_style": "Español mexicano natural, dinámico y claro",
        "scenes": scenes,
        "full_narration": full,
        "call_to_action": "Consulta el precio y los detalles en el enlace.",
        "caption": (
            f"Conoce {name}. Revisa la ficha del vendedor para confirmar "
            "características, precio y disponibilidad. "
            "Este contenido incluye un enlace de afiliado; si compras mediante él, podemos recibir una comisión."
        ),
        "hashtags": ["#FortalezaShopAI", "#TikTokShop", "#EncuentraLoQueBuscas"],
        "generation_mode": "FREE_TEMPLATE",
        "requires_human_review": True,
    }

def _paid_ai_script(product, duration):
    if not config.ENABLE_PAID_AI:
        return None
    if not config.OPENAI_API_KEY:
        raise RuntimeError("ENABLE_PAID_AI está activo pero falta OPENAI_API_KEY. La API puede generar cargos.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("La IA de pago requiere instalar el paquete openai; no es necesario para el modo gratuito.") from exc
    response = OpenAI(api_key=config.OPENAI_API_KEY, timeout=60, max_retries=2).chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Eres guionista de anuncios responsables. Responde solo JSON válido y no inventes datos."},
            {"role": "user", "content": build_script_prompt(product, duration)},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        max_tokens=2200,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("La IA devolvió una respuesta vacía.")
    return json.loads(content)

def validate_script(script, duration):
    required = ("title", "hook", "scenes", "full_narration", "call_to_action", "caption", "hashtags")
    if not isinstance(script, dict):
        raise ValueError("El guion debe ser un objeto.")
    missing = [field for field in required if not script.get(field)]
    if missing:
        raise ValueError("Faltan campos del guion: " + ", ".join(missing))
    scenes = script["scenes"]
    if not isinstance(scenes, list) or not 4 <= len(scenes) <= 7:
        raise ValueError("El guion debe contener entre 4 y 7 escenas.")
    previous_end = 0
    for index, scene in enumerate(scenes, 1):
        if not isinstance(scene, dict):
            raise ValueError(f"La escena {index} no es un objeto.")
        for field in ("start", "end", "visual", "narration", "subtitle"):
            if field not in scene:
                raise ValueError(f"Escena {index}: falta {field}.")
        start, end = int(scene["start"]), int(scene["end"])
        if start < previous_end or start < 0 or end <= start or end > duration:
            raise ValueError(f"Los tiempos de la escena {index} son inválidos.")
        previous_end = end
    if previous_end != duration:
        raise ValueError("Las escenas deben cubrir exactamente la duración del video.")
    return True

def generate_script(product, duration=DEFAULT_DURATION):
    if not validate_product(product):
        raise ValueError("El producto necesita identificador y nombre.")
    duration = int(duration)
    if not MIN_DURATION <= duration <= MAX_DURATION:
        raise ValueError(f"La duración debe estar entre {MIN_DURATION} y {MAX_DURATION} segundos.")
    script = _paid_ai_script(product, duration)
    if script is None:
        script = _offline_script(product, duration)
    validate_script(script, duration)
    return script

def generate_script_id(product_id, hook):
    raw = f"{product_id}|{hook}|{datetime.now(config.TIMEZONE).isoformat()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def is_repeated_hook(hook):
    target = normalize_text(hook)
    return any(normalize_text(item.get("hook")) == target for item in load_script_history())

def save_script(product, script):
    initialize_script_system()
    product_id = _product_id(product)
    script_id = generate_script_id(product_id, script.get("hook", ""))
    output = {
        "script_id": script_id,
        "product_id": product_id,
        "product_name": _product_name(product),
        "product_category": product.get("category", ""),
        "affiliate_url": product.get("affiliate_url") or product.get("affiliate_link", ""),
        "generated_at": datetime.now(config.TIMEZONE).isoformat(),
        "status": "generated",
        "script": script,
    }
    path = SCRIPTS_DIR / f"{script_id}.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)
    history = load_script_history()
    history.append({"script_id": script_id, "product_id": product_id, "product_name": output["product_name"], "hook": script.get("hook"), "generated_at": output["generated_at"]})
    save_script_history(history)
    return output

def process_product(product, duration=DEFAULT_DURATION):
    script = generate_script(product, duration)
    return save_script(product, script)

def generate_unique_script(product, duration=DEFAULT_DURATION, max_attempts=3):
    script = generate_script(product, duration)
    if is_repeated_hook(script["hook"]):
        # El modo sin IA no debe repetir un gancho exacto; añade el nombre al enfoque.
        script["hook"] = f"Una mirada rápida a { _product_name(product) }"
        script["scenes"][0]["narration"] = script["hook"]
        script["full_narration"] = " ".join(s["narration"] for s in script["scenes"])
    validate_script(script, duration)
    return script

def generate_scripts_for_top_products(limit=3, duration=DEFAULT_DURATION):
    results = []
    for product in get_top_products(limit):
        try:
            saved = save_script(product, generate_unique_script(product, duration))
            results.append({"success": True, "script_id": saved["script_id"], "product_name": saved["product_name"], "file": str(SCRIPTS_DIR / f"{saved['script_id']}.json")})
        except Exception as exc:
            logger.exception("Error generando guion para %s", product.get("name"))
            results.append({"success": False, "product_name": product.get("name"), "error": str(exc)})
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(generate_scripts_for_top_products(), ensure_ascii=False, indent=2))
