"""
Gestor seguro de publicaciones.
Prepara borradores y aprobaciones; no publica ni llama APIs externas.
La publicación automática queda bloqueada deliberadamente.
"""
import json
from datetime import datetime
from pathlib import Path
import config

QUEUE_FILE = config.DATA_DIR / "publication_queue.json"

def _load():
    config.initialize_directories()
    if not QUEUE_FILE.exists():
        return []
    try:
        data = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"No se pudo leer la cola de publicaciones: {exc}") from exc

def _save(items):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = QUEUE_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(QUEUE_FILE)

def prepare_draft(product_id, video_path, caption, affiliate_url, disclosure=True):
    if not str(product_id).strip():
        raise ValueError("Falta product_id.")
    video = Path(video_path)
    if not video.is_file() or video.suffix.lower() != ".mp4":
        raise FileNotFoundError("Se requiere un video MP4 existente.")
    if not str(affiliate_url).startswith("https://"):
        raise ValueError("Se requiere un enlace HTTPS de afiliado.")
    if not str(caption).strip():
        raise ValueError("La descripción no puede estar vacía.")
    caption_text = str(caption).strip()
    disclosure_text = "Este contenido incluye un enlace de afiliado. Si compras mediante él, podemos recibir una comisión."
    if disclosure and "enlace de afiliado" not in caption_text.lower():
        caption_text = f"{caption_text}\n\n{disclosure_text}"
    item = {
        "draft_id": f"{product_id}-{datetime.now(config.TIMEZONE).strftime('%Y%m%d%H%M%S')}",
        "product_id": str(product_id),
        "video_path": str(video.resolve()),
        "caption": caption_text,
        "affiliate_url": str(affiliate_url).strip(),
        "affiliate_disclosure_required": bool(disclosure),
        "status": "PENDING_REVIEW",
        "created_at": datetime.now(config.TIMEZONE).isoformat(),
        "published_at": None,
    }
    queue = _load()
    if any(x.get("video_path") == item["video_path"] and x.get("product_id") == item["product_id"] for x in queue):
        raise ValueError("Este video ya está registrado en la cola.")
    queue.append(item)
    _save(queue)
    return item

def list_drafts(status=None):
    items = _load()
    return [x for x in items if status is None or x.get("status") == status]

def approve_draft(draft_id):
    queue = _load()
    for item in queue:
        if item.get("draft_id") == draft_id:
            if item.get("status") != "PENDING_REVIEW":
                raise ValueError("Solo se pueden aprobar borradores pendientes.")
            item["status"] = "APPROVED_MANUAL"
            item["approved_at"] = datetime.now(config.TIMEZONE).isoformat()
            _save(queue)
            return item
    raise KeyError(f"No existe el borrador: {draft_id}")

def publish_draft(draft_id):
    raise RuntimeError(
        "Publicación automática deshabilitada: falta integrar y autorizar la API oficial de la plataforma. "
        "El borrador puede publicarse manualmente desde la app correspondiente."
    )
