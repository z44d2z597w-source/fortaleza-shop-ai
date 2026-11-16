
"""
FORTALEZA SHOP AI
Generador automático de videos verticales.

Crea videos con imágenes, texto y narración.
No utiliza servicios de video de pago.
"""

import json
import logging
import re
from pathlib import Path

import config

logger = logging.getLogger("FORTALEZA_SHOP_AI.video")


VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 24


def create_directories():
    """Prepara las carpetas necesarias."""
    base = Path(config.OUTPUT_DIR)

    folders = {
        "videos": base / "videos",
        "images": base / "images",
        "voices": base / "voices",
        "scripts": base / "scripts",
    }

    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)

    return folders


def safe_filename(value):
    """Genera nombres de archivos seguros."""
    value = re.sub(r"[^\w\-]+", "_", str(value))
    return value.strip("_")[:60] or "video_producto"


def load_script(script_path):
    """Carga un guion JSON."""
    path = Path(script_path)

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el guion: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_scenes(script):
    """Extrae las escenas del guion."""
    if not isinstance(script, dict):
        raise ValueError("El guion debe ser un objeto JSON.")

    scenes = script.get("scenes") or script.get("escenas")

    if not scenes:
        raise ValueError("El guion no contiene escenas.")

    result = []

    for scene in scenes:
        if isinstance(scene, str):
            result.append({
                "text": scene,
                "image": None,
            })
            continue

        if not isinstance(scene, dict):
            continue

        text = (
            scene.get("visual")
            or scene.get("description")
            or scene.get("texto")
            or scene.get("narration")
            or scene.get("voiceover")
            or ""
        )

        image = (
            scene.get("image_path")
            or scene.get("imagen")
            or scene.get("image")
        )

        result.append({
            "text": str(text),
            "image": image,
        })

    if not result:
        raise ValueError("No se encontraron escenas válidas.")

    return result


def resolve_asset(path):
    """Comprueba que un recurso exista."""
    if not path:
        return None

    asset = Path(path)

    if not asset.is_absolute():
        asset = Path(config.BASE_DIR) / asset

    if asset.exists():
        return asset

    return None


def create_video(
    script_path,
    audio_path,
    output_name=None,
):
    """
    Crea un video MP4 vertical a partir de un guion,
    imágenes locales y una narración de audio.

    Las imágenes deben estar preparadas previamente.
    """

    try:
        from moviepy import (
            AudioFileClip,
            ImageClip,
            CompositeVideoClip,
            concatenate_videoclips,
        )

        from PIL import Image, ImageDraw, ImageFont

    except ImportError as error:
        raise RuntimeError(
            "Faltan dependencias. Instala requirements.txt."
        ) from error

    script = load_script(script_path)
    scenes = get_scenes(script)

    audio_file = resolve_asset(audio_path)

    if audio_file is None:
        raise FileNotFoundError(
            f"No se encontró el audio: {audio_path}"
        )

    folders = create_directories()

    if not output_name:
        output_name = Path(script_path).stem

    output_name = safe_filename(output_name)

    output_path = folders["videos"] / f"{output_name}.mp4"

    audio = AudioFileClip(str(audio_file))

    if audio.duration <= 0:
        audio.close()
        raise ValueError("El audio no tiene duración válida.")

    scene_duration = audio.duration / len(scenes)

    clips = []

    try:
        for index, scene in enumerate(scenes):
            image_path = resolve_asset(scene["image"])

            if image_path is None:
                raise FileNotFoundError(
                    f"Falta la imagen de la escena {index + 1}. "
                    "Agrega una imagen local a cada escena."
                )

            # Preparar imagen vertical.
            image = Image.open(image_path).convert("RGB")

            image_ratio = image.width / image.height
            target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT

            if image_ratio > target_ratio:
                new_width = int(image.height * target_ratio)
                left = (image.width - new_width) // 2
                image = image.crop(
                    (left, 0, left + new_width, image.height)
                )
            else:
                new_height = int(image.width / target_ratio)
                top = (image.height - new_height) // 2
                image = image.crop(
                    (0, top, image.width, top + new_height)
                )

            image = image.resize(
                (VIDEO_WIDTH, VIDEO_HEIGHT),
                Image.Resampling.LANCZOS,
            )

            # Agregar texto de escena.
            text = scene["text"].strip()

            if text:
                draw = ImageDraw.Draw(image)

                try:
                    font = ImageFont.truetype(
                        "DejaVuSans-Bold.ttf",
                        58,
                    )
                except OSError:
                    font = ImageFont.load_default()

                max_width = 900
                words = text.split()
                lines = []
                current_line = ""

                for word in words:
                    candidate = (
                        f"{current_line} {word}".strip()
                    )

                    if draw.textbbox(
                        (0, 0),
                        candidate,
                        font=font,
                    )[2] <= max_width:
                        current_line = candidate
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word

                if current_line:
                    lines.append(current_line)

                text_block = "\n".join(lines[:4])

                bbox = draw.multiline_textbbox(
                    (0, 0),
                    text_block,
                    font=font,
                    spacing=14,
                    align="center",
                    stroke_width=3,
                )

                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                x = (VIDEO_WIDTH - text_width) // 2
                y = int(VIDEO_HEIGHT * 0.72)

                draw.rounded_rectangle(
                    (
                        x - 35,
                        y - 25,
                        x + text_width + 35,
                        y + text_height + 25,
                    ),
                    radius=25,
                    fill=(0, 0, 0),
                )

                draw.multiline_text(
                    (x, y),
                    text_block,
                    font=font,
                    fill=(255, 255, 255),
                    spacing=14,
                    align="center",
                    stroke_width=3,
                    stroke_fill=(0, 0, 0),
                )

            # Guardar imagen procesada.
            frame_path = folders["images"] / (
                f"{output_name}_scene_{index + 1}.jpg"
            )

            image.save(frame_path, quality=92)

            clip = ImageClip(str(frame_path)).with_duration(
                scene_duration
            )

            clips.append(clip)

        video = concatenate_videoclips(
            clips,
            method="compose",
        )

        video = video.with_audio(audio)

        video.write_videofile(
            str(output_path),
            fps=VIDEO_FPS,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=2,
            logger=None,
        )

        video.close()

        logger.info("Video creado: %s", output_path)

        return {
            "success": True,
            "video_path": str(output_path),
            "duration": round(audio.duration, 2),
            "resolution": "1080x1920",
            "format": "MP4",
            "cost": 0,
        }

    finally:
        audio.close()

        for clip in clips:
            clip.close()


def check_video_system():
    """Comprueba las dependencias del generador."""

    try:
        import moviepy
        import PIL

        return {
            "available": True,
            "moviepy": moviepy.__version__,
            "pillow": PIL.__version__,
            "resolution": "1080x1920",
            "format": "MP4",
        }

    except ImportError as error:
        return {
            "available": False,
            "error": str(error),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print(
        json.dumps(
            check_video_system(),
            indent=4,
            ensure_ascii=False,
        )
    )