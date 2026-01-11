"""Настройки приложения"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()


class Settings:
    """Настройки приложения"""

    def __init__(self):
        # Telegram Bot
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')

        # vsellm.ru API (опционально)
        self.vsellm_api_key = os.getenv('VSELLM_API_KEY')
        self.vsellm_api_url = os.getenv('VSELLM_API_URL', 'https://api.vsellm.ru/v1')

        # Image settings
        self.default_image_width = int(os.getenv('DEFAULT_IMAGE_WIDTH', '1280'))
        self.default_image_height = int(os.getenv('DEFAULT_IMAGE_HEIGHT', '640'))
        self.image_format = os.getenv('IMAGE_FORMAT', 'PNG')
        self.image_quality = int(os.getenv('IMAGE_QUALITY', '95'))

        # Paths
        self.fonts_dir = os.getenv('FONTS_DIR', './assets/fonts')
        self.backgrounds_dir = os.getenv('BACKGROUNDS_DIR', './assets/backgrounds')
        self.temp_dir = os.getenv('TEMP_DIR', './temp')

        # Валидация обязательных полей
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env файле!")


# Глобальный экземпляр настроек
settings = Settings()
