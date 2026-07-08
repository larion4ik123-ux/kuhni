#!/usr/bin/env python3
"""
Скрипт обработки изображений для production.

Читает assets/raw/ рекурсивно, обрабатывает и создаёт варианты в assets/processed/.
Также генерирует assets/assets-manifest.json с метаданными.

Требования:
- Исправление ориентации по EXIF (ImageOps.exif_transpose)
- Удаление метаданных (EXIF, IPTC, XMP)
- WebP (quality 85) + JPEG fallback (quality 88)
- Варианты: thumbnail (400px), card (800px), hero (1600px), fullscreen (1920px)
- Ограничение максимального размера (fullscreen 1920px по длинной стороне)
- Сохранение пропорций (thumbnail=False, resample=LANCZOS)
- Лёгкая коррекция: яркость +5%, контраст +5%, резкость через UnsharpMask
- НЕ дорисовывать элементы, НЕ менять цвета
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Варианты размеров (по длинной стороне)
VARIANTS = {
    "thumbnail": 400,
    "card": 800,
    "hero": 1600,
    "fullscreen": 1920,
}

# Качество выходных форматов
WEBP_QUALITY = 85
JPEG_QUALITY = 88

# Категории и их подсказки
CATEGORY_SUGGESTED_USAGE: dict[str, str] = {
    "owner": "hero_owner",
    "kitchens": "gallery",
    "kitchens_real": "gallery",
    "facades": "reference",
    "colors": "reference",
    "handles": "reference",
    "countertops": "reference",
    "logo": "logo",
    "brand": "logo",
    "reviews": "review",
}

CLIENT_PHOTO_METADATA: dict[str, dict[str, Any]] = {
    "owner_at_kitchen": {
        "caption": "Артём Ермаков у одной из выполненных кухонь",
        "layout": "corner",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Артём Ермаков на фоне серой кухни на заказ",
        "focus_point": {"x": 0.45, "y": 0.45},
        "suggested_usage": "hero_owner",
    },
    "real_kitchen_light_line": {
        "caption": "Светлая линейная кухня с каменной рабочей зоной",
        "layout": "straight",
        "style": "modern",
        "primary_color": "beige",
        "alt_text": "Светлая кухня на заказ с встроенной техникой",
        "focus_point": {"x": 0.52, "y": 0.45},
    },
    "real_kitchen_green_corner": {
        "caption": "Угловая кухня в спокойном зелёном оттенке",
        "layout": "corner",
        "style": "modern",
        "primary_color": "green",
        "alt_text": "Зелёная угловая кухня на заказ",
        "focus_point": {"x": 0.5, "y": 0.45},
    },
    "real_kitchen_green_long": {
        "caption": "Просторная кухня с зелёными нижними фасадами",
        "layout": "straight",
        "style": "modern",
        "primary_color": "green",
        "alt_text": "Современная кухня с зелёными фасадами и белым верхом",
        "focus_point": {"x": 0.5, "y": 0.42},
    },
    "real_kitchen_graphite_wood": {
        "caption": "Графитовая кухня с тёплой деревянной столешницей",
        "layout": "straight",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Графитовая кухня на заказ с деревянной столешницей",
        "focus_point": {"x": 0.5, "y": 0.46},
    },
    "real_kitchen_soft_gray_corner": {
        "caption": "Угловая кухня в серо-белой гамме",
        "layout": "corner",
        "style": "neoclassic",
        "primary_color": "gray",
        "alt_text": "Серо-белая угловая кухня на заказ",
        "focus_point": {"x": 0.52, "y": 0.45},
    },
    "real_kitchen_classic_white": {
        "caption": "Классическая белая кухня с витринными фасадами",
        "layout": "straight",
        "style": "classic",
        "primary_color": "white",
        "alt_text": "Белая классическая кухня на заказ",
        "focus_point": {"x": 0.5, "y": 0.48},
    },
    "work_4481": {
        "caption": "Светлая кухня с пеналами",
        "style": "modern",
        "primary_color": "beige",
        "alt_text": "Светлая кухня с пеналами и встроенной техникой",
        "focus_point": {"x": 0.52, "y": 0.45},
    },
    "work_4482": {
        "caption": "Угловая кухня с древесной стеновой панелью",
        "layout": "corner",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Угловая кухня с серыми фасадами и древесной стеновой панелью",
        "focus_point": {"x": 0.52, "y": 0.46},
    },
    "work_4485": {
        "caption": "Светлая рабочая зона без ручек",
        "style": "modern",
        "primary_color": "white",
        "alt_text": "Светлая рабочая зона кухни без ручек",
        "focus_point": {"x": 0.48, "y": 0.45},
    },
    "work_4486": {
        "caption": "Угловая кухня с зелёным акцентом",
        "layout": "corner",
        "style": "modern",
        "primary_color": "green",
        "alt_text": "Угловая кухня с зелёными нижними фасадами",
        "focus_point": {"x": 0.5, "y": 0.45},
    },
    "work_4487": {
        "caption": "Фрагмент серой кухни",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Рабочая зона кухни с серыми фасадами",
        "focus_point": {"x": 0.5, "y": 0.46},
    },
    "work_4488": {
        "caption": "Зелёно-белая кухня с длинной рабочей зоной",
        "style": "modern",
        "primary_color": "green",
        "alt_text": "Кухня с зелёными фасадами и светлой столешницей",
        "focus_point": {"x": 0.5, "y": 0.42},
    },
    "work_4489": {
        "caption": "Угловая кухня с встроенной техникой",
        "layout": "corner",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Компактная угловая кухня со встроенной техникой",
        "focus_point": {"x": 0.5, "y": 0.45},
    },
    "work_4490": {
        "caption": "Рабочая линия кухни",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Столешница и варочная зона кухни",
        "focus_point": {"x": 0.5, "y": 0.45},
    },
    "work_4491": {
        "caption": "Угловая кухня с древесной столешницей",
        "layout": "corner",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Угловая кухня в графитовых и древесных оттенках",
        "focus_point": {"x": 0.5, "y": 0.46},
    },
    "work_4492": {
        "caption": "Компактная линейная кухня",
        "layout": "straight",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Компактная линейная кухня в серых оттенках",
        "focus_point": {"x": 0.5, "y": 0.45},
    },
    "work_4493": {
        "caption": "Серо-белая угловая кухня",
        "layout": "corner",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Серо-белая угловая кухня",
        "focus_point": {"x": 0.5, "y": 0.45},
    },
    "work_4494": {
        "caption": "П-образная кухня в зелёном цвете",
        "layout": "u_shape",
        "style": "modern",
        "primary_color": "green",
        "alt_text": "П-образная зелёная кухня в компактном помещении",
        "focus_point": {"x": 0.5, "y": 0.48},
    },
    "work_4495": {
        "caption": "Классическая угловая кухня",
        "layout": "corner",
        "style": "classic",
        "primary_color": "white",
        "alt_text": "Классическая белая угловая кухня",
        "focus_point": {"x": 0.5, "y": 0.46},
    },
    "work_4496": {
        "caption": "Небольшая угловая кухня",
        "layout": "corner",
        "style": "modern",
        "primary_color": "gray",
        "alt_text": "Небольшая угловая кухня в светло-серых оттенках",
        "focus_point": {"x": 0.5, "y": 0.46},
    },
    "logo_interier": {
        "caption": "Логотип мебельного салона Интерьер",
        "alt_text": "Логотип Мебельный салон Интерьер",
        "suggested_usage": "logo",
    },
    "logo_interier_cropped": {
        "caption": "Логотип мебельного салона Интерьер",
        "alt_text": "Логотип Мебельный салон Интерьер",
        "suggested_usage": "logo_header",
    },
}


def _setup_directories(output_root: Path) -> None:
    """Создаёт выходные директории для всех категорий."""
    for category in CATEGORY_SUGGESTED_USAGE:
        (output_root / category).mkdir(parents=True, exist_ok=True)


def _get_category(file_path: Path, input_root: Path) -> str:
    """Определяет категорию из пути относительно input_root."""
    try:
        rel = file_path.relative_to(input_root)
        parts = rel.parts
        if len(parts) >= 2:
            return parts[0]
    except ValueError:
        pass
    return "unknown"


def _get_file_id(file_path: Path) -> str:
    """Возвращает ID файла без расширения."""
    return file_path.stem


def _fix_orientation(img: Image.Image) -> Image.Image:
    """Исправляет ориентацию изображения по EXIF."""
    return ImageOps.exif_transpose(img) or img


def _strip_metadata(img: Image.Image) -> Image.Image:
    """Удаляет все метаданные (EXIF, IPTC, XMP) из изображения."""
    clean = Image.new(img.mode, img.size)
    clean.paste(img)
    return clean


def _apply_light_correction(img: Image.Image) -> Image.Image:
    """Применяет лёгкую коррекцию: яркость +5%, контраст +5%, мягкая резкость."""
    # Яркость +5%
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.05)

    # Контраст +5%
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.05)

    # Резкость — мягкая UnsharpMask
    img = img.filter(
        ImageFilter.UnsharpMask(radius=2, percent=80, threshold=3)
    )

    return img


def _resize_to_long_side(img: Image.Image, max_size: int) -> Image.Image:
    """Уменьшает изображение, чтобы длинная сторона не превышала max_size.

    Сохраняет пропорции, использует LANCZOS.
    """
    w, h = img.size
    long_side = max(w, h)
    if long_side <= max_size:
        return img

    ratio = max_size / long_side
    new_w = int(w * ratio)
    new_h = int(h * ratio)
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def _create_variants(
    img: Image.Image,
    output_dir: Path,
    basename: str,
) -> dict[str, dict[str, Any]]:
    """Создаёт варианты изображения (thumbnail, card, hero, fullscreen) в WebP и JPEG.

    Возвращает словарь с метаданными для каждого варианта.
    """
    variants: dict[str, dict[str, Any]] = {}

    for variant_name, max_size in VARIANTS.items():
        resized = _resize_to_long_side(img, max_size)

        # WebP
        webp_path = output_dir / f"{basename}_{variant_name}.webp"
        # Для WebP конвертируем в RGB если нужно
        webp_img = resized.convert("RGB") if resized.mode in ("RGBA", "LA", "P") else resized
        webp_img.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)

        # JPEG fallback
        jpg_path = output_dir / f"{basename}_{variant_name}.jpg"
        jpg_img = resized.convert("RGB") if resized.mode in ("RGBA", "LA", "P") else resized
        jpg_img.save(jpg_path, "JPEG", quality=JPEG_QUALITY, optimize=True)

        variants[variant_name] = {
            "webp": str(webp_path),
            "jpg": str(jpg_path),
            "width": resized.width,
            "height": resized.height,
        }

        logger.debug("  Вариант %s: %dx%d", variant_name, resized.width, resized.height)

    return variants


def _determine_orientation(width: int, height: int) -> str:
    """Определяет ориентацию изображения."""
    if width > height:
        return "landscape"
    elif height > width:
        return "portrait"
    return "square"


def _is_real_work(category: str) -> bool:
    """Определяет, является ли изображение реальной работой (не placeholder)."""
    return category == "kitchens_real"


def _get_quality(category: str) -> str:
    """Возвращает качество изображения."""
    if category in ("kitchens_real", "brand"):
        return "client_photo"
    return "placeholder"


def _is_suitable_for_hero(category: str) -> bool:
    """Определяет, подходит ли изображение для hero-секции."""
    return category in ("owner", "kitchens", "kitchens_real", "logo", "brand")


def _is_suitable_for_gallery(category: str) -> bool:
    """Определяет, подходит ли изображение для галереи."""
    return category in ("kitchens", "kitchens_real")


def _is_suitable_for_ai_reference(category: str) -> bool:
    """Определяет, подходит ли изображение для AI-референса."""
    return category in ("kitchens", "kitchens_real", "facades", "colors", "handles", "countertops")


def process_file(
    file_path: Path,
    input_root: Path,
    output_root: Path,
    display_order: int,
) -> dict[str, Any] | None:
    """Обрабатывает один файл изображения.

    Возвращает запись для манифеста или None, если файл пропущен.
    """
    # Пропускаем не-изображения и .gitkeep
    if file_path.name.startswith("."):
        logger.debug("Пропуск скрытого файла: %s", file_path)
        return None

    ext = file_path.suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"):
        logger.debug("Пропуск не-изображения: %s", file_path)
        return None

    category = _get_category(file_path, input_root)
    file_id = _get_file_id(file_path)
    basename = file_path.stem

    logger.info("Обработка: %s (категория: %s)", file_path, category)

    try:
        with Image.open(file_path) as img:
            # Исправляем ориентацию
            img = _fix_orientation(img)

            # Удаляем метаданные
            img = _strip_metadata(img)

            # Лёгкая коррекция
            img = _apply_light_correction(img)

            # Определяем выходную директорию
            output_dir = output_root / category
            output_dir.mkdir(parents=True, exist_ok=True)

            # Создаём варианты
            variants = _create_variants(img, output_dir, basename)

            # Определяем ориентацию по исходному размеру (fullscreen вариант)
            fullscreen_info = variants.get("fullscreen", variants.get("hero", variants.get("card")))
            orientation = _determine_orientation(
                fullscreen_info["width"],
                fullscreen_info["height"],
            )

            # Формируем запись манифеста
            entry: dict[str, Any] = {
                "id": file_id,
                "source_path": str(file_path),
                "category": category,
                "orientation": orientation,
                "variants": variants,
                "suggested_usage": CATEGORY_SUGGESTED_USAGE.get(category, "general"),
                "quality": _get_quality(category),
                "suitable_for_hero": _is_suitable_for_hero(category),
                "suitable_for_gallery": _is_suitable_for_gallery(category),
                "suitable_for_ai_reference": _is_suitable_for_ai_reference(category),
                "caption": "",
                "layout": "",
                "style": "",
                "primary_color": "",
                "alt_text": "",
                "focus_point": {"x": 0.5, "y": 0.5},
                "display_order": display_order,
                "is_real_work": _is_real_work(category),
            }

            entry.update(CLIENT_PHOTO_METADATA.get(file_id, {}))

            return entry

    except Exception as e:
        logger.error("Ошибка обработки %s: %s", file_path, e)
        return None


def collect_image_files(input_root: Path) -> list[Path]:
    """Рекурсивно собирает все файлы изображений из input_root."""
    image_files: list[Path] = []

    if not input_root.exists():
        logger.warning("Входная директория не существует: %s", input_root)
        return image_files

    for root, _dirs, files in os.walk(input_root):
        for filename in sorted(files):
            file_path = Path(root) / filename
            ext = file_path.suffix.lower()
            if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"):
                image_files.append(file_path)

    # Сортируем для детерминированного порядка
    image_files.sort()
    return image_files


def write_manifest(manifest_path: Path, entries: list[dict[str, Any]]) -> None:
    """Записывает манифест в JSON."""
    manifest = {"files": entries}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    logger.info("Манифест записан: %s (%d записей)", manifest_path, len(entries))


def main() -> int:
    """Главная функция скрипта обработки изображений."""
    parser = argparse.ArgumentParser(
        description="Обработка изображений для production",
    )
    parser.add_argument(
        "--input",
        default="assets/raw",
        help="Входная директория с изображениями (по умолчанию: assets/raw)",
    )
    parser.add_argument(
        "--output",
        default="assets/processed",
        help="Выходная директория для обработанных изображений (по умолчанию: assets/processed)",
    )
    parser.add_argument(
        "--manifest",
        default="assets/assets-manifest.json",
        help="Путь к файлу манифеста (по умолчанию: assets/assets-manifest.json)",
    )
    args = parser.parse_args()

    # Определяем абсолютные пути
    project_root = Path(__file__).resolve().parent.parent
    input_root = project_root / args.input
    output_root = project_root / args.output
    manifest_path = project_root / args.manifest

    logger.info("Входная директория:  %s", input_root)
    logger.info("Выходная директория: %s", output_root)
    logger.info("Манифест:            %s", manifest_path)

    # Проверяем существование входной директории
    if not input_root.exists():
        logger.warning("Входная директория не существует: %s", input_root)
        logger.warning("Создаю директорию...")
        input_root.mkdir(parents=True, exist_ok=True)

    # Создаём выходные директории
    _setup_directories(output_root)

    # Собираем файлы
    image_files = collect_image_files(input_root)
    logger.info("Найдено изображений: %d", len(image_files))

    if not image_files:
        logger.warning("Нет изображений для обработки!")
        # Записываем пустой манифест
        write_manifest(manifest_path, [])
        return 0

    # Обрабатываем файлы
    entries: list[dict[str, Any]] = []
    for display_order, file_path in enumerate(image_files, start=1):
        entry = process_file(file_path, input_root, output_root, display_order)
        if entry:
            entries.append(entry)

    # Записываем манифест
    write_manifest(manifest_path, entries)

    logger.info("Обработка завершена. Всего записей в манифесте: %d", len(entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
