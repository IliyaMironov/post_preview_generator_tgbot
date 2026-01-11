"""Клавиатуры для Telegram бота"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_style_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора стиля превью"""
    keyboard = [
        [
            InlineKeyboardButton("✨ Минимализм", callback_data="style_minimal"),
            InlineKeyboardButton("🌈 Градиент", callback_data="style_gradient"),
        ],
        [
            InlineKeyboardButton("🎨 С иллюстрацией (AI)", callback_data="style_ai"),
            InlineKeyboardButton("🖼 Свой фон", callback_data="style_custom"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Сгенерировать", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Отмена", callback_data="confirm_no"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_gradient_colors_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора цветовой схемы для градиента"""
    keyboard = [
        [
            InlineKeyboardButton("🌅 Закат", callback_data="gradient_sunset"),
            InlineKeyboardButton("🌊 Океан", callback_data="gradient_ocean"),
        ],
        [
            InlineKeyboardButton("🌸 Розовый", callback_data="gradient_pink"),
            InlineKeyboardButton("🌲 Лес", callback_data="gradient_forest"),
        ],
        [
            InlineKeyboardButton("🌃 Ночь", callback_data="gradient_night"),
            InlineKeyboardButton("🔥 Огонь", callback_data="gradient_fire"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
