
"""
FORTALEZA SHOP AI
Generador gratuito de voz para videos.

Utiliza Edge TTS.
No requiere una API de pago.
Necesita conexión a internet.
"""

import asyncio
import json
import logging
import re
from pathlib import Path

import edge_tts

import config


logger = logging.getLogger("FORTALEZA_SHOP_AI.voice")


# Voces disponibles en español de México.
VOICES = {
    "femenina": "es-MX-DaliaNeural",
    "masculina": "es-MX-JorgeNeural",
}

DEFAULT_VOICE = "femenina"
DEFAULT_RATE = "+0%"
DEFAULT_VOLUME = "+0%"


def initialize_voice_directories():
    """Crea la carpeta donde se guardarán las voces."""
    voice_dir = Path(config.OUTPUT_DIR) / "voices"
    voice_dir.mkdir(parents=True, exist_ok=True)
    return voice_dir


def load_script(script_path):
    """Carga un guion desde un archivo JSON."""
    path = Path(script_path)

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el guion: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_narration(script):
    """
    Extrae la narración del guion.
    Acepta distintos formatos de escenas.
    """
    if isinstance(script, str):
        narration = script

    elif isinstance(script, dict):
        narration = (
            script.get("narration")
            or script.get("voiceover")
            or script.get("voz")
            or script.get("narracion")
            or script.get("texto_voz")
        )

        if not narration:
            scenes = (
                script.get("scenes")
                or script.get("escenas")
                or []
            )

            parts = []

            for scene in scenes:
                if isinstance(scene, str):
                    parts.append(scene)
                    continue

                if not isinstance(scene, dict):
                    continue

                text = (
                    scene.get("narration")
                    or scene.get("voiceover")
                    or scene.get("voz")
                    or scene.get("narracion")
                    or scene.get("voice_text")
                )

                if text:
                    parts.append(str(text))

            narration = " ".join(parts)

    else:
        narration = None

    if not narration:
        raise ValueError(
            "El guion no contiene texto para generar voz."
        )

    narration = re.sub(r"\s+", " ", str(narration)).strip()

    if len(narration) < 5:
        raise ValueError("La narración es demasiado corta.")

    return narration


def safe_filename(text):
    """Convierte un texto en un nombre de archivo seguro."""
    text = re.sub(r"[^\w\-]+", "_", text, flags=re.UNICODE)
    return text.strip("_")[:60] or "voz_producto"


async def generate_voice_async(
    narration,
    output_path,
    voice=DEFAULT_VOICE,
    rate=DEFAULT_RATE,
    volume=DEFAULT_VOLUME,
):
    """Genera el archivo de audio mediante Edge TTS."""

    voice_id = VOICES.get(voice, VOICES[DEFAULT_VOICE])

    communicate = edge_tts.Communicate(
        text=narration,
        voice=voice_id,
        rate=rate,
        volume=volume,
    )

    await communicate.save(str(output_path))

    return output_path


def generate_voice(
    script,
    filename=None,
    voice=DEFAULT_VOICE,
):
    """
    Genera la voz de un guion.

    script puede ser:
    - Un diccionario con el contenido del guion.
    - Una cadena de texto.
    """

    narration = extract_narration(script)

    voice_dir = initialize_voice_directories()

    if not filename:
        if isinstance(script, dict):
            filename = (
                script.get("product_name")
                or script.get("producto")
                or script.get("title")
                or "voz_producto"
            )
        else:
            filename = "voz_producto"

    filename = safe_filename(filename)

    output_path = voice_dir / f"{filename}.mp3"

    asyncio.run(
        generate_voice_async(
            narration=narration,
            output_path=output_path,
            voice=voice,
        )
    )

    logger.info("Voz generada: %s", output_path)

    return {
        "success": True,
        "audio_path": str(output_path),
        "voice": VOICES.get(voice, VOICES[DEFAULT_VOICE]),
        "characters": len(narration),
        "cost": 0,
    }


def generate_voice_from_file(
    script_path,
    voice=DEFAULT_VOICE,
):
    """Genera voz directamente desde un JSON guardado."""

    script = load_script(script_path)

    filename = Path(script_path).stem

    return generate_voice(
        script=script,
        filename=filename,
        voice=voice,
    )


def check_voice_system():
    """Comprueba que la herramienta esté instalada."""

    try:
        import edge_tts

        return {
            "available": True,
            "engine": "Edge TTS",
            "cost": 0,
            "internet_required": True,
            "voices": list(VOICES.keys()),
        }

    except ImportError:
        return {
            "available": False,
            "engine": None,
            "error": "Instala edge-tts para utilizar el generador.",
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    status = check_voice_system()

    print(json.dumps(status, indent=4, ensure_ascii=False))
