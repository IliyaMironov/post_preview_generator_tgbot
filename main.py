"""Главный файл Telegram бота для генерации превью"""

import logging
import os
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from config import settings
from bot.handlers import (
    start,
    help_command,
    new_preview,
    style_chosen,
    gradient_color_chosen,
    custom_background_received,
    skip_custom_background,
    title_received,
    description_received,
    skip_description,
    cancel,
)
from bot.states import (
    CHOOSING_STYLE,
    ENTERING_TITLE,
    ENTERING_DESCRIPTION,
    UPLOADING_CUSTOM_BG,
)


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Запуск бота"""

    # Создаем необходимые директории
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(settings.fonts_dir, exist_ok=True)
    os.makedirs(settings.backgrounds_dir, exist_ok=True)

    # Создаем приложение
    application = Application.builder().token(settings.telegram_bot_token).build()

    # ConversationHandler для создания превью
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('new', new_preview)],
        states={
            CHOOSING_STYLE: [
                CallbackQueryHandler(gradient_color_chosen, pattern='^gradient_'),
                CallbackQueryHandler(style_chosen, pattern='^style_'),
            ],
            UPLOADING_CUSTOM_BG: [
                MessageHandler(filters.PHOTO, custom_background_received),
                CommandHandler('skip', skip_custom_background),
            ],
            ENTERING_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, title_received),
            ],
            ENTERING_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, description_received),
                CommandHandler('skip', skip_description),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Регистрируем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(conv_handler)

    # Запускаем бота
    logger.info("🤖 Бот запущен!")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == '__main__':
    main()
