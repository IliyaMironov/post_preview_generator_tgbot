"""Шаблоны для генерации изображений"""

from typing import Tuple


class ColorScheme:
    """Цветовые схемы для градиентов"""

    SUNSET = {
        "start": (255, 94, 77),    # Красный
        "end": (255, 177, 66),     # Оранжевый
    }

    OCEAN = {
        "start": (34, 193, 195),   # Бирюзовый
        "end": (45, 134, 253),     # Синий
    }

    PINK = {
        "start": (253, 121, 168),  # Розовый
        "end": (184, 113, 255),    # Фиолетовый
    }

    FOREST = {
        "start": (67, 198, 172),   # Зеленый
        "end": (25, 122, 122),     # Темно-зеленый
    }

    NIGHT = {
        "start": (47, 53, 66),     # Темно-серый
        "end": (30, 34, 43),       # Почти черный
    }

    FIRE = {
        "start": (235, 51, 36),    # Красный
        "end": (244, 92, 67),      # Оранжево-красный
    }


def get_gradient_colors(gradient_type: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Получить цвета градиента по типу"""
    gradients = {
        "sunset": ColorScheme.SUNSET,
        "ocean": ColorScheme.OCEAN,
        "pink": ColorScheme.PINK,
        "forest": ColorScheme.FOREST,
        "night": ColorScheme.NIGHT,
        "fire": ColorScheme.FIRE,
    }

    colors = gradients.get(gradient_type, ColorScheme.OCEAN)
    return colors["start"], colors["end"]


class TemplateConfig:
    """Конфигурация шаблонов"""

    # Размеры изображения
    WIDTH = 1280
    HEIGHT = 640

    # Отступы
    PADDING = 60
    TITLE_Y_POSITION = 250
    DESCRIPTION_Y_POSITION = 380

    # Размеры шрифтов
    TITLE_FONT_SIZE = 72
    DESCRIPTION_FONT_SIZE = 36

    # Цвета для минимализма
    MINIMAL_BG_LIGHT = (255, 255, 255)  # Белый
    MINIMAL_BG_DARK = (30, 30, 30)      # Темно-серый
    MINIMAL_TEXT_LIGHT = (30, 30, 30)   # Темный текст
    MINIMAL_TEXT_DARK = (255, 255, 255) # Светлый текст
    MINIMAL_ACCENT = (100, 100, 255)    # Синий акцент

    # Полупрозрачный overlay для читаемости текста
    OVERLAY_ALPHA = 180
