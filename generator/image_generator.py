"""Гибридный генератор изображений: OpenCV для графики + PIL для текста с кириллицей"""

import os
import cv2
import numpy as np
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from .templates import TemplateConfig, get_gradient_colors


class ImageGenerator:
    """Генератор превью-изображений (OpenCV + PIL)"""

    def __init__(self, fonts_dir: str = "./assets/fonts"):
        self.fonts_dir = fonts_dir
        self.width = TemplateConfig.WIDTH
        self.height = TemplateConfig.HEIGHT

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Получить шрифт PIL для кириллицы"""
        # Пытаемся загрузить пользовательский шрифт
        font_name = "Arial-Bold.ttf" if bold else "Arial.ttf"
        font_path = os.path.join(self.fonts_dir, font_name)

        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except Exception:
            pass

        # Fallback на системные шрифты Windows
        try:
            system_font = "arialbd.ttf" if bold else "arial.ttf"
            return ImageFont.truetype(system_font, size)
        except Exception:
            pass

        # Последний fallback - дефолтный шрифт
        return ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """Разбить текст на строки по ширине"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _cv2_to_pil(self, cv_image: np.ndarray) -> Image.Image:
        """Конвертировать OpenCV image (BGR) в PIL Image (RGB)"""
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)

    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Конвертировать PIL Image (RGB) в OpenCV image (BGR)"""
        rgb_array = np.array(pil_image)
        return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)

    def _create_gradient(self, start_color: Tuple[int, int, int],
                        end_color: Tuple[int, int, int]) -> np.ndarray:
        """Создать вертикальный градиент с OpenCV"""
        # OpenCV использует BGR вместо RGB
        start_bgr = (start_color[2], start_color[1], start_color[0])
        end_bgr = (end_color[2], end_color[1], end_color[0])

        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        for y in range(self.height):
            ratio = y / self.height
            b = int(start_bgr[0] * (1 - ratio) + end_bgr[0] * ratio)
            g = int(start_bgr[1] * (1 - ratio) + end_bgr[1] * ratio)
            r = int(start_bgr[2] * (1 - ratio) + end_bgr[2] * ratio)
            img[y, :] = [b, g, r]

        return img

    def generate_minimal(self, title: str, description: Optional[str] = None,
                        dark_mode: bool = False) -> BytesIO:
        """Генерация минималистичного превью"""
        # Цвета
        bg_color = TemplateConfig.MINIMAL_BG_DARK if dark_mode else TemplateConfig.MINIMAL_BG_LIGHT
        text_color = TemplateConfig.MINIMAL_TEXT_DARK if dark_mode else TemplateConfig.MINIMAL_TEXT_LIGHT
        accent_color = TemplateConfig.MINIMAL_ACCENT

        # Создаем изображение с OpenCV (BGR)
        bg_bgr = (bg_color[2], bg_color[1], bg_color[0])
        cv_img = np.full((self.height, self.width, 3), bg_bgr, dtype=np.uint8)

        # Акцентная линия слева
        line_width = 8
        accent_bgr = (accent_color[2], accent_color[1], accent_color[0])
        cv2.rectangle(cv_img, (0, 0), (line_width, self.height), accent_bgr, -1)

        # Конвертируем в PIL для рисования текста
        pil_img = self._cv2_to_pil(cv_img)
        draw = ImageDraw.Draw(pil_img)

        # Шрифты
        title_font = self._get_font(TemplateConfig.TITLE_FONT_SIZE, bold=True)
        desc_font = self._get_font(TemplateConfig.DESCRIPTION_FONT_SIZE, bold=False)

        # Рисуем заголовок
        max_text_width = self.width - TemplateConfig.PADDING * 2 - line_width * 2
        title_lines = self._wrap_text(title, title_font, max_text_width)

        y = TemplateConfig.TITLE_Y_POSITION
        for line in title_lines:
            draw.text(
                (TemplateConfig.PADDING + line_width * 2, y),
                line,
                font=title_font,
                fill=text_color
            )
            y += TemplateConfig.TITLE_FONT_SIZE + 10

        # Рисуем описание
        if description:
            y += 40
            desc_lines = self._wrap_text(description, desc_font, max_text_width)
            for line in desc_lines:
                draw.text(
                    (TemplateConfig.PADDING + line_width * 2, y),
                    line,
                    font=desc_font,
                    fill=text_color
                )
                y += TemplateConfig.DESCRIPTION_FONT_SIZE + 8

        # Сохраняем в BytesIO
        output = BytesIO()
        pil_img.save(output, format='PNG')
        output.seek(0)
        return output

    def generate_gradient(self, title: str, description: Optional[str] = None,
                         gradient_type: str = "ocean") -> BytesIO:
        """Генерация превью с градиентом"""
        # Получаем цвета градиента
        start_color, end_color = get_gradient_colors(gradient_type)

        # Создаем градиент с OpenCV
        cv_img = self._create_gradient(start_color, end_color)

        # Конвертируем в PIL для текста
        pil_img = self._cv2_to_pil(cv_img)
        draw = ImageDraw.Draw(pil_img)

        # Шрифты
        title_font = self._get_font(TemplateConfig.TITLE_FONT_SIZE, bold=True)
        desc_font = self._get_font(TemplateConfig.DESCRIPTION_FONT_SIZE, bold=False)
        text_color = (255, 255, 255)
        shadow_color = (0, 0, 0)

        # Рисуем заголовок с тенью
        max_text_width = self.width - TemplateConfig.PADDING * 2
        title_lines = self._wrap_text(title, title_font, max_text_width)

        y = TemplateConfig.TITLE_Y_POSITION
        for line in title_lines:
            # Тень
            draw.text(
                (TemplateConfig.PADDING + 2, y + 2),
                line,
                font=title_font,
                fill=shadow_color
            )
            # Основной текст
            draw.text(
                (TemplateConfig.PADDING, y),
                line,
                font=title_font,
                fill=text_color
            )
            y += TemplateConfig.TITLE_FONT_SIZE + 10

        # Рисуем описание
        if description:
            y += 40
            desc_lines = self._wrap_text(description, desc_font, max_text_width)
            for line in desc_lines:
                # Тень
                draw.text(
                    (TemplateConfig.PADDING + 2, y + 2),
                    line,
                    font=desc_font,
                    fill=shadow_color
                )
                # Основной текст
                draw.text(
                    (TemplateConfig.PADDING, y),
                    line,
                    font=desc_font,
                    fill=text_color
                )
                y += TemplateConfig.DESCRIPTION_FONT_SIZE + 8

        # Сохраняем в BytesIO
        output = BytesIO()
        pil_img.save(output, format='PNG')
        output.seek(0)
        return output

    def generate_ai_only(self, ai_image: np.ndarray) -> BytesIO:
        """
        Генерация превью из чистого AI-изображения без текста
        с правильным масштабированием (crop to fit)

        Args:
            ai_image: AI-сгенерированное изображение (numpy array)

        Returns:
            BytesIO с PNG изображением
        """
        # Получаем размеры исходного изображения
        img_height, img_width = ai_image.shape[:2]

        # Вычисляем соотношения сторон
        target_ratio = self.width / self.height  # 1280/640 = 2.0
        img_ratio = img_width / img_height

        # Масштабируем так, чтобы заполнить целевой размер
        if img_ratio > target_ratio:
            # Изображение шире целевого - масштабируем по высоте
            new_height = self.height
            new_width = int(img_width * (self.height / img_height))
        else:
            # Изображение уже или равно целевому - масштабируем по ширине
            new_width = self.width
            new_height = int(img_height * (self.width / img_width))

        # Масштабируем изображение
        resized = cv2.resize(ai_image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)

        # Обрезаем до нужного размера (центрируем)
        if new_width > self.width:
            # Обрезаем по ширине
            x_offset = (new_width - self.width) // 2
            cv_img = resized[:, x_offset:x_offset + self.width]
        elif new_height > self.height:
            # Обрезаем по высоте
            y_offset = (new_height - self.height) // 2
            cv_img = resized[y_offset:y_offset + self.height, :]
        else:
            cv_img = resized

        # Конвертируем в PIL
        pil_img = self._cv2_to_pil(cv_img)

        # Сохраняем в BytesIO
        output = BytesIO()
        pil_img.save(output, format='PNG')
        output.seek(0)
        return output

    def generate_with_background(self, title: str, description: Optional[str] = None,
                                 background_path: Optional[str] = None,
                                 background_image: Optional[np.ndarray] = None,
                                 add_text: bool = True) -> BytesIO:
        """Генерация превью с пользовательским фоном"""
        # Загружаем фон
        if background_image is not None:
            cv_img = background_image.copy()
        elif background_path and os.path.exists(background_path):
            cv_img = cv2.imread(background_path)
            if cv_img is None:
                return self.generate_gradient(title, description)
        else:
            return self.generate_gradient(title, description)

        # Масштабируем фон
        cv_img = cv2.resize(cv_img, (self.width, self.height), interpolation=cv2.INTER_LANCZOS4)

        # Конвертируем в PIL
        pil_img = self._cv2_to_pil(cv_img)

        # Добавляем текст только если нужно
        if add_text:
            # Добавляем полупрозрачный overlay для читаемости текста
            overlay = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            alpha = TemplateConfig.OVERLAY_ALPHA / 255.0
            cv_img = cv2.addWeighted(cv_img, 1 - alpha, overlay, alpha, 0)
            pil_img = self._cv2_to_pil(cv_img)

            draw = ImageDraw.Draw(pil_img)

            # Шрифты
            title_font = self._get_font(TemplateConfig.TITLE_FONT_SIZE, bold=True)
            desc_font = self._get_font(TemplateConfig.DESCRIPTION_FONT_SIZE, bold=False)
            text_color = (255, 255, 255)

            # Рисуем заголовок
            max_text_width = self.width - TemplateConfig.PADDING * 2
            title_lines = self._wrap_text(title, title_font, max_text_width)

            y = TemplateConfig.TITLE_Y_POSITION
            for line in title_lines:
                draw.text(
                    (TemplateConfig.PADDING, y),
                    line,
                    font=title_font,
                    fill=text_color
                )
                y += TemplateConfig.TITLE_FONT_SIZE + 10

            # Рисуем описание
            if description:
                y += 40
                desc_lines = self._wrap_text(description, desc_font, max_text_width)
                for line in desc_lines:
                    draw.text(
                        (TemplateConfig.PADDING, y),
                        line,
                        font=desc_font,
                        fill=text_color
                    )
                    y += TemplateConfig.DESCRIPTION_FONT_SIZE + 8

        # Сохраняем в BytesIO
        output = BytesIO()
        pil_img.save(output, format='PNG')
        output.seek(0)
        return output
