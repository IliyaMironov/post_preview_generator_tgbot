"""AI-генерация изображений через vsellm.ru API"""

import base64
import requests
import cv2
import numpy as np
from typing import Optional
from io import BytesIO


class AIImageGenerator:
    """Генератор изображений через vsellm.ru API"""

    def __init__(self, api_key: str, api_url: str = "https://api.vsellm.ru/v1"):
        self.api_key = api_key
        self.api_url = api_url
        # Используем google/gemini-2.5-flash-image - проверенная рабочая модель
        self.model = "google/gemini-2.5-flash-image"

    def generate_illustration(self, prompt: str, size: str = "1024x1024") -> Optional[np.ndarray]:
        """
        Генерация AI-иллюстрации

        Args:
            prompt: Текстовое описание для генерации
            size: Размер изображения (например, "1024x1024")
                  Примечание: Gemini модели могут не поддерживать все размеры

        Returns:
            OpenCV numpy array или None в случае ошибки
        """
        try:
            # vsellm.ru использует chat/completions для генерации изображений
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 4096
                },
                timeout=90
            )

            response.raise_for_status()
            data = response.json()

            # Извлекаем base64 изображение из ответа
            choices = data.get('choices', [])
            if not choices:
                print("Ошибка: пустой ответ от API")
                return None

            message = choices[0].get('message', {})
            images = message.get('images', [])

            if not images:
                print("Ошибка: изображение не сгенерировано")
                return None

            # Получаем data URL
            image_data_url = images[0].get('image_url', {}).get('url', '')

            if not image_data_url.startswith('data:image'):
                print("Ошибка: неверный формат изображения")
                return None

            # Извлекаем base64 данные
            # Формат: data:image/png;base64,<base64_data>
            base64_data = image_data_url.split(',', 1)[1]

            # Декодируем base64
            image_bytes = base64.b64decode(base64_data)

            # Конвертируем в OpenCV image (numpy array)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            return image

        except requests.exceptions.Timeout:
            print("Ошибка: таймаут при генерации изображения")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка HTTP при генерации AI-изображения: {e}")
            return None
        except Exception as e:
            print(f"Ошибка при генерации AI-изображения: {e}")
            return None

    def create_prompt_from_title(self, title: str, description: str = None) -> str:
        """
        Создать промпт для AI-генерации на основе заголовка и описания

        Args:
            title: Заголовок поста
            description: Описание поста (опционально)

        Returns:
            Промпт для генерации изображения
        """
        # Промпт для мемной, привлекательной иллюстрации в стиле Telegram каналов
        # base_prompt = (
        #     "Generate an eye-catching, modern illustration for a Telegram channel post preview. "
        #     "Style: bold, vibrant, slightly humorous/meme-style but still professional. "
        #     "Use bright colors and dynamic composition. "
        #     "NO TEXT, NO LETTERS, NO WORDS in the image - only visual elements. "
        #     "Focus on creating a memorable, engaging visual that represents the topic. "
        #     "Similar to popular Telegram channel previews - clean but attention-grabbing. "
        # )
        base_prompt = (
            "Generate a highly engaging, meme-style illustration for a Telegram channel post preview. "
            "Style: realistic, cinematic look with real human characters (photorealistic or semi-photorealistic). "
            "Humor: subtle, clever, situational humor — expressive facial emotions, ironic or relatable moments. "
            "People should look natural and believable, not cartoonish. "
            "Composition: dynamic, close-up or medium shot, strong focus on emotions and reactions. "
            "Mood: light, playful, witty, slightly ironic — like a smart visual joke. "
            "Use natural lighting, depth of field, and realistic textures. "
            "Bright but not oversaturated colors, modern aesthetic. "
            "NO TEXT, NO LETTERS, NO WORDS in the image — humor must be purely visual. "
            "The image should instantly tell a funny or relatable story without explanation. "
            "Perfect for a viral Telegram channel preview: clean, modern, emotionally engaging, and memorable."
        )

        # Добавляем тему из заголовка и описания
        if description:
            prompt = f"{base_prompt}Topic: {title}. Context: {description}"
        else:
            prompt = f"{base_prompt}Topic: {title}"

        return prompt
