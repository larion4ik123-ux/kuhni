#!/usr/bin/env python3
"""
Генератор детерминированных placeholder-изображений для платформы «Мебельный салон Интерьер».

Создаёт синтетические изображения в assets/raw/ для разработки.
Все значения фиксированы (без random), чтобы повторный запуск давал идентичный результат.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Корневая директория проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_RAW = PROJECT_ROOT / "assets" / "raw"

# Размеры изображений
SIZE_OWNER: Tuple[int, int] = (1200, 1500)       # вертикальный портрет
SIZE_KITCHEN: Tuple[int, int] = (1600, 1200)     # горизонтальная кухня
SIZE_SAMPLE: Tuple[int, int] = (800, 600)        # образцы
SIZE_LOGO: Tuple[int, int] = (400, 120)          # логотип

# Качество JPEG
JPEG_QUALITY = 90

# Цветовая палитра (нейтральные, детерминированные)
COLOR_BG_LIGHT = (245, 245, 242)
COLOR_BG_WARM = (250, 248, 245)
COLOR_BG_GRAY = (235, 235, 235)
COLOR_BG_DARK = (45, 45, 50)
COLOR_GRAPHITE = (60, 60, 65)
COLOR_RED_ACCENT = (180, 50, 50)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (20, 20, 20)
COLOR_GRAY = (128, 128, 128)
COLOR_BEIGE = (210, 200, 185)
COLOR_GREEN = (100, 130, 100)
COLOR_WOOD_LIGHT = (200, 175, 145)
COLOR_WOOD_DARK = (140, 110, 80)
COLOR_STONE = (185, 185, 180)
COLOR_COUNTER_LIGHT = (250, 250, 248)
COLOR_FLOOR = (200, 195, 185)


def _ensure_dir(path: Path) -> None:
    """Создаёт директорию, если она не существует."""
    path.mkdir(parents=True, exist_ok=True)


def _save_jpeg(img: Image.Image, path: Path, quality: int = JPEG_QUALITY) -> None:
    """Сохраняет изображение в JPEG с указанным качеством."""
    rgb = img.convert("RGB") if img.mode in ("RGBA", "LA", "P") else img
    rgb.save(path, "JPEG", quality=quality, optimize=True)
    logger.info("Сохранено: %s (%dx%d)", path, img.width, img.height)


def _save_png(img: Image.Image, path: Path) -> None:
    """Сохраняет изображение в PNG."""
    img.save(path, "PNG", optimize=True)
    logger.info("Сохранено: %s (%dx%d)", path, img.width, img.height)


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Возвращает шрифт заданного размера."""
    try:
        # Пробуем системные шрифты
        for font_path in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    return ImageFont.load_default()


# ──────────────────────────────────────────────────────────────────────────────
# Генераторы изображений
# ──────────────────────────────────────────────────────────────────────────────

def generate_owner() -> None:
    """Генерирует placeholder портрета владельца."""
    _ensure_dir(ASSETS_RAW / "owner")
    path = ASSETS_RAW / "owner" / "owner.jpg"

    w, h = SIZE_OWNER
    img = Image.new("RGB", (w, h), COLOR_BG_WARM)
    draw = ImageDraw.Draw(img)

    # Фон с мягким градиентом (детерминированный)
    for y in range(h):
        factor = y / h
        r = int(250 - factor * 15)
        g = int(248 - factor * 12)
        b = int(245 - factor * 10)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Силуэт фигуры (овальная голова + трапеция тела)
    head_cx, head_cy = w // 2, h // 3
    head_rx, head_ry = 140, 160
    draw.ellipse(
        [head_cx - head_rx, head_cy - head_ry, head_cx + head_rx, head_cy + head_ry],
        fill=COLOR_GRAY,
    )

    # Плечи / тело
    body_top = head_cy + head_ry - 20
    body_bottom = h - 100
    draw.polygon(
        [
            (w // 2 - 200, body_top),
            (w // 2 + 200, body_top),
            (w // 2 + 280, body_bottom),
            (w // 2 - 280, body_bottom),
        ],
        fill=(100, 100, 105),
    )

    # Рамка
    draw.rectangle([0, 0, w - 1, h - 1], outline=COLOR_GRAPHITE, width=4)

    _save_jpeg(img, path)


def generate_logo() -> None:
    """Генерирует placeholder логотипа с текстом."""
    _ensure_dir(ASSETS_RAW / "logo")
    path = ASSETS_RAW / "logo" / "logo.png"

    w, h = SIZE_LOGO
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Белый фон (для preview)
    draw.rectangle([0, 0, w - 1, h - 1], fill=(255, 255, 255, 255))

    font = _get_font(20)
    font_small = _get_font(12)

    # Основной текст — графитовый
    text = "ИНТЕРЬЕР"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (w - text_w) // 2
    y = (h - text_h) // 2 - 5
    draw.text((x, y), text, fill=COLOR_GRAPHITE, font=font)

    # Красный акцент — подчёркивание
    line_y = y + text_h + 4
    line_margin = 40
    draw.line(
        [(line_margin, line_y), (w - line_margin, line_y)],
        fill=COLOR_RED_ACCENT,
        width=3,
    )

    # Подпись
    sub = "мебельный салон"
    bbox_sub = draw.textbbox((0, 0), sub, font=font_small)
    sub_w = bbox_sub[2] - bbox_sub[0]
    draw.text(((w - sub_w) // 2, line_y + 8), sub, fill=COLOR_GRAY, font=font_small)

    _save_png(img, path)


def _draw_cabinet(
    draw: ImageDraw.ImageDraw,
    x1: int, y1: int, x2: int, y2: int,
    color: Tuple[int, int, int],
    handle_color: Tuple[int, int, int] = COLOR_BLACK,
    has_handle: bool = True,
) -> None:
    """Рисует один фасад кухонного шкафа."""
    draw.rectangle([x1, y1, x2, y2], fill=color, outline=(180, 180, 180), width=1)
    if has_handle:
        hx = (x1 + x2) // 2
        hy = y1 + 15
        draw.ellipse([hx - 3, hy - 3, hx + 3, hy + 3], fill=handle_color)


def _draw_countertop(
    draw: ImageDraw.ImageDraw,
    x1: int, y1: int, x2: int, y2: int,
    color: Tuple[int, int, int],
) -> None:
    """Рисует столешницу."""
    draw.rectangle([x1, y1, x2, y2], fill=color, outline=(160, 160, 160), width=1)
    # Блик
    draw.line([(x1 + 5, y1 + 3), (x2 - 5, y1 + 3)], fill=(255, 255, 255, 128), width=2)


def _draw_floor(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    """Рисует пол."""
    floor_y = int(h * 0.78)
    draw.rectangle([0, floor_y, w - 1, h - 1], fill=COLOR_FLOOR)
    # Плитка
    for x in range(0, w, 120):
        draw.line([(x, floor_y), (x, h - 1)], fill=(190, 185, 175), width=1)
    for y in range(floor_y, h, 80):
        draw.line([(0, y), (w - 1, y)], fill=(190, 185, 175), width=1)


def _draw_wall(draw: ImageDraw.ImageDraw, w: int, h: int, color: Tuple[int, int, int]) -> None:
    """Рисует стену."""
    wall_h = int(h * 0.78)
    draw.rectangle([0, 0, w - 1, wall_h], fill=color)


def _draw_window(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int) -> None:
    """Рисует окно."""
    draw.rectangle([x1, y1, x2, y2], fill=(220, 230, 240), outline=(180, 180, 180), width=2)
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    draw.line([(cx, y1), (cx, y2)], fill=(180, 180, 180), width=2)
    draw.line([(x1, cy), (x2, cy)], fill=(180, 180, 180), width=2)


def generate_kitchen(index: int) -> None:
    """Генерирует одно placeholder-изображение кухни."""
    _ensure_dir(ASSETS_RAW / "kitchens")
    path = ASSETS_RAW / "kitchens" / f"kitchen_{index:02d}.jpg"

    w, h = SIZE_KITCHEN
    img = Image.new("RGB", (w, h), COLOR_BG_LIGHT)
    draw = ImageDraw.Draw(img)

    # Параметры по индексу (детерминированные)
    layouts = [
        "straight",   # 01 — прямая
        "corner",     # 02 — угловая
        "u_shape",    # 03 — П-образная
        "island",     # 04 — с островом
        "straight",   # 05 — прямая
        "corner",     # 06 — угловая
    ]
    styles = [
        "modern",      # 01
        "neoclassic",  # 02
        "classic",     # 03
        "modern",      # 04
        "neoclassic",  # 05
        "classic",     # 06
    ]
    facade_colors = [
        COLOR_WHITE,   # 01
        COLOR_BEIGE,    # 02
        COLOR_GREEN,     # 03
        COLOR_GRAY,      # 04
        COLOR_WHITE,     # 05
        COLOR_BEIGE,     # 06
    ]
    wall_colors = [
        (235, 235, 235),
        (240, 238, 235),
        (230, 235, 230),
        (245, 245, 245),
        (238, 236, 233),
        (232, 237, 232),
    ]
    countertop_colors = [
        COLOR_COUNTER_LIGHT,
        COLOR_STONE,
        COLOR_WOOD_LIGHT,
        COLOR_COUNTER_LIGHT,
        COLOR_STONE,
        COLOR_WOOD_LIGHT,
    ]

    layout = layouts[index - 1]
    style = styles[index - 1]
    fcolor = facade_colors[index - 1]
    wcolor = wall_colors[index - 1]
    ccolor = countertop_colors[index - 1]

    # Стена и пол
    _draw_wall(draw, w, h, wcolor)
    _draw_floor(draw, w, h)

    # Окно
    _draw_window(draw, w // 2 - 200, 80, w // 2 + 200, 280)

    # Верхние шкафы
    cabinet_h = 160
    cabinet_depth = 60
    countertop_h = 30
    base_h = 180
    y_counter = int(h * 0.78) - base_h - countertop_h
    y_top = y_counter - 200

    if layout == "straight":
        # Нижний ряд
        for i in range(6):
            x1 = 100 + i * 220
            x2 = x1 + 200
            _draw_cabinet(draw, x1, y_counter, x2, y_counter + base_h, fcolor)
        # Столешница
        _draw_countertop(draw, 90, y_counter - countertop_h, 100 + 6 * 220 - 10, y_counter, ccolor)
        # Верхний ряд
        for i in range(5):
            x1 = 120 + i * 220
            x2 = x1 + 180
            _draw_cabinet(draw, x1, y_top, x2, y_top + cabinet_h, fcolor)

    elif layout == "corner":
        # Левая стена
        for i in range(3):
            x1 = 80 + i * 200
            x2 = x1 + 180
            _draw_cabinet(draw, x1, y_counter, x2, y_counter + base_h, fcolor)
        _draw_countertop(draw, 70, y_counter - countertop_h, 80 + 3 * 200, y_counter, ccolor)
        # Угловой шкаф
        _draw_cabinet(draw, 80 + 3 * 200 - 20, y_counter, 80 + 3 * 200 + 180, y_counter + base_h, fcolor)
        # Правая стена (вертикально вниз)
        for i in range(2):
            y1 = y_counter + i * 190
            y2 = y1 + 170
            _draw_cabinet(draw, 80 + 3 * 200 + 160, y1, 80 + 3 * 200 + 160 + 180, y2, fcolor)
        # Верхние
        for i in range(3):
            x1 = 100 + i * 200
            x2 = x1 + 160
            _draw_cabinet(draw, x1, y_top, x2, y_top + cabinet_h, fcolor)

    elif layout == "u_shape":
        # Левая стена
        for i in range(2):
            x1 = 60 + i * 180
            x2 = x1 + 160
            _draw_cabinet(draw, x1, y_counter, x2, y_counter + base_h, fcolor)
        # Задняя стена
        for i in range(3):
            x1 = 60 + 2 * 180 + i * 200
            x2 = x1 + 180
            _draw_cabinet(draw, x1, y_counter, x2, y_counter + base_h, fcolor)
        # Правая стена
        for i in range(2):
            x1 = 60 + 2 * 180 + 3 * 200 + i * 180
            x2 = x1 + 160
            _draw_cabinet(draw, x1, y_counter, x2, y_counter + base_h, fcolor)
        # Столешница
        _draw_countertop(draw, 50, y_counter - countertop_h, x2 + 10, y_counter, ccolor)
        # Верхние
        for i in range(4):
            x1 = 80 + i * 200
            x2 = x1 + 160
            _draw_cabinet(draw, x1, y_top, x2, y_top + cabinet_h, fcolor)

    elif layout == "island":
        # Задняя стена
        for i in range(5):
            x1 = 120 + i * 220
            x2 = x1 + 200
            _draw_cabinet(draw, x1, y_counter, x2, y_counter + base_h, fcolor)
        _draw_countertop(draw, 110, y_counter - countertop_h, 120 + 5 * 220 - 10, y_counter, ccolor)
        # Остров
        island_x = w // 2 - 200
        island_y = y_counter + 120
        draw.rectangle([island_x, island_y, island_x + 400, island_y + 120], fill=ccolor, outline=(160, 160, 160), width=2)
        # Верхние
        for i in range(4):
            x1 = 140 + i * 220
            x2 = x1 + 180
            _draw_cabinet(draw, x1, y_top, x2, y_top + cabinet_h, fcolor)

    # Стильные детали
    if style == "classic":
        # Карниз
        draw.rectangle([80, y_top - 20, w - 80, y_top], fill=(210, 200, 185), outline=(180, 170, 160), width=1)
    elif style == "modern":
        # Подсветка под верхними шкафами
        draw.rectangle([100, y_top + cabinet_h, w - 100, y_top + cabinet_h + 4], fill=(255, 250, 220))

    # Рамка
    draw.rectangle([0, 0, w - 1, h - 1], outline=(200, 200, 200), width=2)

    # Подпись стиля (для разработки)
    font = _get_font(16)
    label = f"{style.capitalize()} | {layout.replace('_', '-')}"
    draw.text((20, h - 40), label, fill=(150, 150, 150), font=font)

    _save_jpeg(img, path)


def generate_facade(name: str, color: Tuple[int, int, int]) -> None:
    """Генерирует placeholder образца фасада."""
    _ensure_dir(ASSETS_RAW / "facades")
    path = ASSETS_RAW / "facades" / f"{name}.jpg"

    w, h = SIZE_SAMPLE
    img = Image.new("RGB", (w, h), color)
    draw = ImageDraw.Draw(img)

    # Текстура — мелкие линии для имитации дерева/фактуры
    for y in range(0, h, 8):
        shade = 10 if y % 16 == 0 else -5
        line_color = (
            max(0, min(255, color[0] + shade)),
            max(0, min(255, color[1] + shade)),
            max(0, min(255, color[2] + shade)),
        )
        draw.line([(0, y), (w, y)], fill=line_color, width=1)

    # Рамка
    draw.rectangle([0, 0, w - 1, h - 1], outline=(180, 180, 180), width=3)

    # Название
    font = _get_font(18)
    label = name.replace("facade_", "").replace("_", " ").title()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    # Подложка под текст
    pad = 8
    draw.rectangle(
        [(w - text_w - pad * 2) // 2, h - text_h - pad * 2 - 20, (w + text_w + pad * 2) // 2, h - 20],
        fill=(255, 255, 255, 200),
    )
    draw.text(((w - text_w) // 2, h - text_h - 20 - pad), label, fill=COLOR_BLACK, font=font)

    _save_jpeg(img, path)


def generate_color(name: str, color: Tuple[int, int, int]) -> None:
    """Генерирует placeholder образца цвета."""
    _ensure_dir(ASSETS_RAW / "colors")
    path = ASSETS_RAW / "colors" / f"{name}.jpg"

    w, h = SIZE_SAMPLE
    img = Image.new("RGB", (w, h), color)
    draw = ImageDraw.Draw(img)

    # Рамка
    draw.rectangle([0, 0, w - 1, h - 1], outline=(200, 200, 200), width=4)

    # Название цвета
    font = _get_font(20)
    label = name.replace("color_", "").replace("_", " ").title()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(((w - text_w) // 2, (h - text_h) // 2), label, fill=COLOR_BLACK, font=font)

    _save_jpeg(img, path)


def generate_handle(name: str) -> None:
    """Генерирует placeholder образца ручки."""
    _ensure_dir(ASSETS_RAW / "handles")
    path = ASSETS_RAW / "handles" / f"{name}.jpg"

    w, h = SIZE_SAMPLE
    img = Image.new("RGB", (w, h), COLOR_BG_GRAY)
    draw = ImageDraw.Draw(img)

    cx, cy = w // 2, h // 2

    if name == "handle_scoop":
        # Вытянутая выемка
        draw.rectangle([cx - 80, cy - 10, cx + 80, cy + 10], fill=(50, 50, 50), outline=(30, 30, 30), width=2)
        draw.rectangle([cx - 80, cy - 10, cx + 80, cy - 5], fill=(80, 80, 80))
    elif name == "handle_square_black":
        # Квадратная ручка
        draw.rectangle([cx - 25, cy - 25, cx + 25, cy + 25], fill=COLOR_BLACK, outline=(40, 40, 40), width=2)
        draw.rectangle([cx - 15, cy - 15, cx + 15, cy + 15], fill=(60, 60, 60))
    elif name == "handle_button":
        # Круглая кнопка
        draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(70, 70, 70), outline=(50, 50, 50), width=2)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(120, 120, 120))
    elif name == "handle_gola":
        # Профиль Gola — длинная горизонтальная полоса
        draw.rectangle([cx - 120, cy - 6, cx + 120, cy + 6], fill=(55, 55, 55), outline=(35, 35, 35), width=1)
        draw.rectangle([cx - 120, cy - 6, cx + 120, cy - 2], fill=(90, 90, 90))

    # Подложка (фасад)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([cx - 150, cy - 100, cx + 150, cy + 100], fill=(200, 200, 200, 180), outline=(160, 160, 160), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Рамка
    draw.rectangle([0, 0, w - 1, h - 1], outline=(180, 180, 180), width=3)

    _save_jpeg(img, path)


def generate_countertop(name: str, color: Tuple[int, int, int]) -> None:
    """Генерирует placeholder образца столешницы."""
    _ensure_dir(ASSETS_RAW / "countertops")
    path = ASSETS_RAW / "countertops" / f"{name}.jpg"

    w, h = SIZE_SAMPLE
    img = Image.new("RGB", (w, h), color)
    draw = ImageDraw.Draw(img)

    if name == "countertop_wood":
        # Текстура дерева — горизонтальные линии
        for y in range(0, h, 6):
            shade = 12 if y % 12 == 0 else -4
            line_color = (
                max(0, min(255, color[0] + shade)),
                max(0, min(255, color[1] + shade)),
                max(0, min(255, color[2] + shade)),
            )
            draw.line([(0, y), (w, y)], fill=line_color, width=1)
    elif name == "countertop_stone":
        # Текстура камня — мелкие пятна/зернистость
        for x in range(0, w, 20):
            for y in range(0, h, 20):
                shade = 15 if (x + y) % 40 == 0 else -8
                spot_color = (
                    max(0, min(255, color[0] + shade)),
                    max(0, min(255, color[1] + shade)),
                    max(0, min(255, color[2] + shade)),
                )
                draw.ellipse([x, y, x + 12, y + 8], fill=spot_color)
    elif name == "countertop_light":
        # Лёгкая глянцевая — блик
        draw.polygon([(w // 2 - 100, 50), (w // 2 + 100, 50), (w // 2 + 60, 150), (w // 2 - 60, 150)], fill=(255, 255, 255, 128))

    # Рамка
    draw.rectangle([0, 0, w - 1, h - 1], outline=(180, 180, 180), width=3)

    # Название
    font = _get_font(18)
    label = name.replace("countertop_", "").replace("_", " ").title()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(((w - text_w) // 2, h - text_h - 20), label, fill=COLOR_BLACK, font=font)

    _save_jpeg(img, path)


def generate_reviews_gitkeep() -> None:
    """Создаёт .gitkeep в директории reviews."""
    _ensure_dir(ASSETS_RAW / "reviews")
    gitkeep = ASSETS_RAW / "reviews" / ".gitkeep"
    gitkeep.touch(exist_ok=True)
    logger.info("Создан: %s", gitkeep)


def main() -> None:
    """Главная функция: генерирует все placeholder-изображения."""
    logger.info("Начинаю генерацию placeholder-изображений...")
    logger.info("Целевая директория: %s", ASSETS_RAW)

    # Владелец
    generate_owner()

    # Логотип
    generate_logo()

    # Кухни (6 штук)
    for i in range(1, 7):
        generate_kitchen(i)

    # Фасады
    generate_facade("facade_interno", COLOR_WHITE)
    generate_facade("facade_agt", COLOR_BEIGE)
    generate_facade("facade_classic", COLOR_GREEN)

    # Цвета
    generate_color("color_gray", COLOR_GRAY)
    generate_color("color_beige", COLOR_BEIGE)
    generate_color("color_green", COLOR_GREEN)
    generate_color("color_white", COLOR_WHITE)

    # Ручки
    generate_handle("handle_scoop")
    generate_handle("handle_square_black")
    generate_handle("handle_button")
    generate_handle("handle_gola")

    # Столешницы
    generate_countertop("countertop_light", COLOR_COUNTER_LIGHT)
    generate_countertop("countertop_wood", COLOR_WOOD_LIGHT)
    generate_countertop("countertop_stone", COLOR_STONE)

    # Reviews
    generate_reviews_gitkeep()

    logger.info("Генерация завершена. Все файлы созданы в %s", ASSETS_RAW)


if __name__ == "__main__":
    main()
