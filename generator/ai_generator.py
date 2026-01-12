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
        # self.model = "google/gemini-2.5-flash-image"
        self.model = "google/gemini-3-pro-image-preview"
        # self.model = "gemini-3-pro-image"

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
                timeout=180
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
            "Create a MEME-STYLE visual for Telegram post - should look like a reaction meme or internet culture reference. "
            "Style: Choose ONE of these approaches that fits the topic best: "
            "1) Famous movie/TV scene recreation (like popular meme templates) "
            "2) Exaggerated facial expression or reaction shot (close-up, dramatic) "
            "3) Absurd/surreal situation that makes people laugh "
            "4) 'That moment when...' relatable situation "
            "Requirements: "
            "- Must be INSTANTLY recognizable as a meme, not a stock photo "
            "- Focus on ONE strong emotion or reaction (shock, confusion, joy, despair, etc) "
            "- Exaggerate the emotion - make it dramatic and memorable "
            "- Use unusual angles, dramatic lighting, or cinematic framing "
            "- The image should make people SMILE or LAUGH immediately "
            "- Avoid generic corporate/business stock photo aesthetics "
            "- NO TEXT, NO LETTERS, NO WORDS - only pure visual humor "
            "- Should work WITHOUT context but become perfect WITH the post title "
            "Think: popular Russian/internet memes, reaction images, cultural references. "
            "Make it SHAREABLE, RELATABLE, and MEMEABLE."
        )

        # Добавляем контекст для более мемного результата
        context_hint = self._get_meme_context_hint(title, description)

        # Добавляем тему из заголовка и описания
        if description:
            prompt = f"{base_prompt}\n\n{context_hint}\n\nTopic: {title}. Context: {description}"
        else:
            prompt = f"{base_prompt}\n\n{context_hint}\n\nTopic: {title}"

        return prompt

    def _get_meme_context_hint(self, title: str, description: str = None) -> str:
        """
        Подсказка для AI на основе контекста поста

        Args:
            title: Заголовок поста
            description: Описание поста

        Returns:
            Подсказка для стиля мема
        """
        text = (title + " " + (description or "")).lower()

        # Определяем тип эмоции/ситуации
        if any(word in text for word in ["не получается", "провал", "ошибка", "упала", "падает", "кризис"]):
            return "Suggested meme style: Disappointed/frustrated reaction. Think: facepalm, head in hands, 'why me' expression."

        elif any(word in text for word in ["успех", "получилось", "победа", "рост", "выиграл"]):
            return "Suggested meme style: Victory/celebration reaction. Think: triumphant pose, happy dance, 'yes!' moment."

        elif any(word in text for word in ["удивительно", "неожиданно", "шок", "wow", "офигеть"]):
            return "Suggested meme style: Shocked/surprised reaction. Think: wide eyes, dropped jaw, pointing at something."

        elif any(word in text for word in ["думаю", "размышление", "вопрос", "как", "почему"]):
            return "Suggested meme style: Thinking/confused reaction. Think: scratching head, looking puzzled, contemplating."

        elif any(word in text for word in ["работа", "офис", "начальник", "коллеги", "совещание"]):
            return "Suggested meme style: Office/work situation. Think: office worker's relatable moment, meeting scene, desk drama."

        elif any(word in text for word in ["деньги", "продаж", "клиент", "бизнес", "прибыль"]):
            return "Suggested meme style: Money/business related. Think: counting money, empty wallet, negotiation scene."

        elif any(word in text for word in ["учимся", "обучение", "новое", "не знал", "узнал"]):
            return "Suggested meme style: Learning/discovery moment. Think: 'aha!' moment, mind blown, taking notes intensely."

        else:
            return "Suggested meme style: Universal relatable reaction. Make it expressive and dramatic."
