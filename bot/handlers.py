"""Обработчики команд и сообщений Telegram бота"""

import os
import cv2
import numpy as np
from io import BytesIO
from typing import Optional
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from .states import (
    CHOOSING_STYLE,
    ENTERING_TITLE,
    ENTERING_DESCRIPTION,
    UPLOADING_CUSTOM_BG,
    CONFIRMING,
)
from .keyboards import (
    get_style_keyboard,
    get_gradient_colors_keyboard,
)
from generator.image_generator import ImageGenerator
from generator.ai_generator import AIImageGenerator
from config import settings


# Инициализация генераторов
image_generator = ImageGenerator(settings.fonts_dir)
ai_generator = None

# AI-генератор только если ключ валиден (не placeholder и не пустой)
if settings.vsellm_api_key and not settings.vsellm_api_key.startswith('__n8n_BLANK_VALUE'):
    try:
        ai_generator = AIImageGenerator(settings.vsellm_api_key, settings.vsellm_api_url)
        print("[INFO] AI-генератор инициализирован")
    except Exception as e:
        print(f"[WARNING] Не удалось инициализировать AI-генератор: {e}")
        ai_generator = None
else:
    print("[INFO] AI-генерация отключена (ключ не настроен)")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_message = (
        "👋 Привет! Я помогу тебе создавать красивые превью для постов в Telegram.\n\n"
        "🎨 Доступные команды:\n"
        "/new - Создать новое превью\n"
        "/help - Справка\n\n"
        "Давай начнем! Используй /new чтобы создать первое превью."
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_message = (
        "📖 Как пользоваться ботом:\n\n"
        "1️⃣ Отправь команду /new\n"
        "2️⃣ Выбери стиль оформления\n"
        "3️⃣ Введи заголовок поста\n"
        "4️⃣ Введи описание (или пропусти)\n"
        "5️⃣ Получи готовое изображение!\n\n"
        "🎨 Доступные стили:\n"
        "• Минимализм - чистый дизайн с акцентом\n"
        "• Градиент - современный градиентный фон\n"
        "• С иллюстрацией - AI-генерация (если настроено)\n"
        "• Свой фон - загрузи свое изображение\n\n"
        "💡 Советы:\n"
        "• Заголовок должен быть кратким и емким\n"
        "• Описание помогает раскрыть тему\n"
        "• Используйте разные стили для разнообразия\n"
    )
    await update.message.reply_text(help_message)


async def new_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало создания нового превью"""
    # Очищаем предыдущие данные
    context.user_data.clear()

    await update.message.reply_text(
        "🎨 Отлично! Давай создадим превью для твоего поста.\n\n"
        "Сначала выбери стиль оформления:",
        reply_markup=get_style_keyboard()
    )
    return CHOOSING_STYLE


async def style_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора стиля"""
    query = update.callback_query
    await query.answer()

    style = query.data.replace("style_", "")
    context.user_data['style'] = style

    # Если выбран градиент, предлагаем выбрать цветовую схему
    if style == "gradient":
        await query.edit_message_text(
            "🌈 Выбери цветовую схему градиента:",
            reply_markup=get_gradient_colors_keyboard()
        )
        return CHOOSING_STYLE  # Остаемся в том же состоянии

    # Если выбран пользовательский фон
    if style == "custom":
        await query.edit_message_text(
            "🖼 Отлично! Загрузи изображение, которое хочешь использовать в качестве фона.\n\n"
            "Или отправь /skip чтобы использовать градиент по умолчанию."
        )
        return UPLOADING_CUSTOM_BG

    # Если выбран AI-стиль, но AI не настроен
    if style == "ai" and not ai_generator:
        await query.edit_message_text(
            "⚠️ AI-генерация недоступна (не настроен API ключ vsellm.ru).\n"
            "Используем градиент вместо этого."
        )
        context.user_data['style'] = 'gradient'
        context.user_data['gradient_type'] = 'ocean'

    # Просим ввести заголовок
    await query.edit_message_text(
        f"✅ Стиль выбран: {get_style_name(style)}\n\n"
        "Теперь введи заголовок для превью:"
    )
    return ENTERING_TITLE


async def gradient_color_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора цвета градиента"""
    query = update.callback_query
    await query.answer()

    gradient_type = query.data.replace("gradient_", "")
    context.user_data['gradient_type'] = gradient_type

    await query.edit_message_text(
        f"✅ Градиент выбран: {get_gradient_name(gradient_type)}\n\n"
        "Теперь введи заголовок для превью:"
    )
    return ENTERING_TITLE


async def custom_background_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка загрузки пользовательского фона"""
    if update.message.photo:
        # Получаем фото в лучшем качестве
        photo = update.message.photo[-1]
        file = await photo.get_file()

        # Сохраняем во временную директорию
        os.makedirs(settings.temp_dir, exist_ok=True)
        file_path = os.path.join(settings.temp_dir, f"bg_{update.effective_user.id}.jpg")
        await file.download_to_drive(file_path)

        context.user_data['custom_bg_path'] = file_path

        await update.message.reply_text(
            "✅ Фон загружен!\n\n"
            "Теперь введи заголовок для превью:"
        )
        return ENTERING_TITLE
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, отправь изображение или используй /skip"
        )
        return UPLOADING_CUSTOM_BG


async def skip_custom_background(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пропуск загрузки пользовательского фона"""
    context.user_data['style'] = 'gradient'
    context.user_data['gradient_type'] = 'ocean'

    await update.message.reply_text(
        "Используем градиент по умолчанию.\n\n"
        "Введи заголовок для превью:"
    )
    return ENTERING_TITLE


async def title_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка заголовка"""
    title = update.message.text
    context.user_data['title'] = title

    await update.message.reply_text(
        "✅ Заголовок сохранен!\n\n"
        "Теперь введи описание (или отправь /skip чтобы пропустить):"
    )
    return ENTERING_DESCRIPTION


async def description_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка описания"""
    description = update.message.text
    context.user_data['description'] = description

    await update.message.reply_text("⏳ Генерирую превью...")
    await generate_and_send(update, context)
    return ConversationHandler.END


async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пропуск описания"""
    await update.message.reply_text("⏳ Генерирую превью...")
    await generate_and_send(update, context)
    return ConversationHandler.END


async def generate_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерация и отправка изображения"""
    title = context.user_data.get('title', 'Заголовок')
    description = context.user_data.get('description')
    style = context.user_data.get('style', 'gradient')

    try:
        # Генерируем изображение в зависимости от стиля
        if style == 'minimal':
            image_bytes = image_generator.generate_minimal(title, description)
        elif style == 'gradient':
            gradient_type = context.user_data.get('gradient_type', 'ocean')
            image_bytes = image_generator.generate_gradient(title, description, gradient_type)
        elif style == 'custom':
            bg_path = context.user_data.get('custom_bg_path')
            image_bytes = image_generator.generate_with_background(title, description, bg_path)
        elif style == 'ai' and ai_generator:
            # AI-генерация (мемный стиль без текста)
            prompt = ai_generator.create_prompt_from_title(title, description)
            ai_image = ai_generator.generate_illustration(prompt)
            if ai_image is not None:
                # Используем чистое AI-изображение без текста
                image_bytes = image_generator.generate_ai_only(ai_image)
            else:
                # Fallback на градиент если AI не сработал
                image_bytes = image_generator.generate_gradient(title, description)
        else:
            # Fallback
            image_bytes = image_generator.generate_gradient(title, description)

        # Отправляем изображение
        await update.message.reply_photo(
            photo=image_bytes,
            caption=f"✅ Готово! Твое превью для поста:\n\n📝 {title}"
        )

        # Очищаем временные файлы
        if 'custom_bg_path' in context.user_data:
            bg_path = context.user_data['custom_bg_path']
            if os.path.exists(bg_path):
                os.remove(bg_path)

    except Exception as e:
        await update.message.reply_text(
            f"❌ Произошла ошибка при генерации: {str(e)}\n\n"
            "Попробуй снова с помощью /new"
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена создания превью"""
    await update.message.reply_text(
        "❌ Создание превью отменено.\n\n"
        "Используй /new чтобы начать заново."
    )
    context.user_data.clear()
    return ConversationHandler.END


def get_style_name(style: str) -> str:
    """Получить читаемое название стиля"""
    names = {
        'minimal': '✨ Минимализм',
        'gradient': '🌈 Градиент',
        'ai': '🎨 С иллюстрацией (AI)',
        'custom': '🖼 Свой фон',
    }
    return names.get(style, style)


def get_gradient_name(gradient_type: str) -> str:
    """Получить читаемое название градиента"""
    names = {
        'sunset': '🌅 Закат',
        'ocean': '🌊 Океан',
        'pink': '🌸 Розовый',
        'forest': '🌲 Лес',
        'night': '🌃 Ночь',
        'fire': '🔥 Огонь',
    }
    return names.get(gradient_type, gradient_type)
