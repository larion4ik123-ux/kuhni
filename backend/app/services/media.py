"""Safe image uploads for editable site blocks and gallery items."""

from __future__ import annotations

import hashlib
import io
import secrets
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError

from backend.app.core.security import safe_filename
from backend.app.core.settings import Settings
from backend.app.models import MediaFile


async def store_uploaded_image(
    upload: UploadFile,
    settings: Settings,
    *,
    category: str,
    is_real_work: bool = False,
) -> MediaFile:
    """Validate, resize and persist a customer-provided raster image."""
    limit = settings.MAX_UPLOAD_MB * 1024 * 1024
    raw = await upload.read(limit + 1)
    if not raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл пуст")
    if len(raw) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл больше {settings.MAX_UPLOAD_MB} МБ",
        )

    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужна фотография JPG, PNG или WebP",
        ) from exc

    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
    width, height = image.size

    token = secrets.token_hex(12)
    relative_dir = Path("uploads") / category
    media_dir = Path(settings.MEDIA_DIR)
    target_dir = media_dir / relative_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    jpg_relative = relative_dir / f"{token}.jpg"
    webp_relative = relative_dir / f"{token}.webp"
    image.save(media_dir / jpg_relative, "JPEG", quality=90, optimize=True)
    image.save(media_dir / webp_relative, "WEBP", quality=88, method=6)

    return MediaFile(
        category=category[:32],
        original_filename=safe_filename(upload.filename or "image.jpg"),
        stored_path=jpg_relative.as_posix(),
        jpg_path=jpg_relative.as_posix(),
        webp_path=webp_relative.as_posix(),
        mime="image/jpeg",
        width=width,
        height=height,
        size_bytes=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(),
        is_real_work=is_real_work,
    )
