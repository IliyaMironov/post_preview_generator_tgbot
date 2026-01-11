"""Генератор изображений с использованием OpenCV"""

import os
import cv2
import numpy as np
from io import BytesIO
from typing import Optional, Tuple
from .templates import TemplateConfig, get_gradient_colors


class ImageGenerator:
    """Генератор превью-изображений"""

    def __init__(self, fonts_dir: str = "./assets/fonts"):
        self.fonts_dir = fonts_dir
        self.width = TemplateConfig.WIDTH
        self.height = TemplateConfig.HEIGHT
        # OpenCV использует cv2.FONT_HERSHEY для встроенных шрифтов
        self.font_face = cv2.FONT_HERSHEY_SIMPLEX
        self.font_face_bold = cv2.FONT_HERSHEY_DUPLEX

    def _wrap_text(self, text: str, font_scale: float, thickness: int, max_width: int) -> list[str]:
        """Разбить текст на строки по ширине"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            (text_width, _), _ = cv2.getTextSize(test_line, self.font_face_bold, font_scale, thickness)

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _create_gradient(self, start_color: Tuple[int, int, int],
                        end_color: Tuple[int, int, int]) -> np.ndarray:
        """Создать вертикальный градиент"""
        # OpenCV использует BGR вместо RGB
        start_bgr = (start_color[2], start_color[1], start_color[0])
        end_bgr = (end_color[2], end_color[1], end_color[0])

        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        for y in range(self.height):
            # Интерполяция между start и end цветами
            ratio = y / self.height
            b = int(start_bgr[0] * (1 - ratio) + end_bgr[0] * ratio)
            g = int(start_bgr[1] * (1 - ratio) + end_bgr[1] * ratio)
            r = int(start_bgr[2] * (1 - ratio) + end_bgr[2] * ratio)
            img[y, :] = [b, g, r]

        return img

    def _put_text_with_shadow(self, img: np.ndarray, text: str, position: Tuple[int, int],
                              font_scale: float, color: Tuple[int, int, int],
                              thickness: int, shadow: bool = False):
        """Нарисовать текст с опциональной тенью"""
        # Конвертируем RGB в BGR для OpenCV
        color_bgr = (color[2], color[1], color[0])

        if shadow:
            # Рисуем тень
            shadow_color = (0, 0, 0)
            cv2.putText(img, text, (position[0] + 2, position[1] + 2),
                       self.font_face_bold, font_scale, shadow_color, thickness, cv2.LINE_AA)

        # Рисуем основной текст
        cv2.putText(img, text, position, self.font_face_bold, font_scale,
                   color_bgr, thickness, cv2.LINE_AA)

    def generate_minimal(self, title: str, description: Optional[str] = None,
                        dark_mode: bool = False) -> BytesIO:
        """Генерация минималистичного превью"""
        # Цвета
        bg_color = TemplateConfig.MINIMAL_BG_DARK if dark_mode else TemplateConfig.MINIMAL_BG_LIGHT
        text_color = TemplateConfig.MINIMAL_TEXT_DARK if dark_mode else TemplateConfig.MINIMAL_TEXT_LIGHT
        accent_color = TemplateConfig.MINIMAL_ACCENT

        # Создаем изображение (BGR для OpenCV)
        bg_bgr = (bg_color[2], bg_color[1], bg_color[0])
        img = np.full((self.height, self.width, 3), bg_bgr, dtype=np.uint8)

        # Акцентная линия слева
        line_width = 8
        accent_bgr = (accent_color[2], accent_color[1], accent_color[0])
        cv2.rectangle(img, (0, 0), (line_width, self.height), accent_bgr, -1)

        # Параметры шрифта
        title_font_scale = 1.8
        desc_font_scale = 0.9
        title_thickness = 3
        desc_thickness = 2

        # Рисуем заголовок
        max_text_width = self.width - TemplateConfig.PADDING * 2 - line_width * 2
        title_lines = self._wrap_text(title, title_font_scale, title_thickness, max_text_width)

        y = TemplateConfig.TITLE_Y_POSITION
        for line in title_lines:
            self._put_text_with_shadow(img, line, (TemplateConfig.PADDING + line_width * 2, y),
                                       title_font_scale, text_color, title_thickness, shadow=False)
            y += 80

        # Рисуем описание
        if description:
            y += 20
            desc_lines = self._wrap_text(description, desc_font_scale, desc_thickness, max_text_width)
            for line in desc_lines:
                self._put_text_with_shadow(img, line, (TemplateConfig.PADDING + line_width * 2, y),
                                           desc_font_scale, text_color, desc_thickness, shadow=False)
                y += 50

        # Конвертируем в PNG и возвращаем BytesIO
        _, buffer = cv2.imencode('.png', img)
        output = BytesIO(buffer.tobytes())
        output.seek(0)
        return output

    def generate_gradient(self, title: str, description: Optional[str] = None,
                         gradient_type: str = "ocean") -> BytesIO:
        """Генерация превью с градиентом"""
        # Получаем цвета градиента
        start_color, end_color = get_gradient_colors(gradient_type)

        # Создаем градиент
        img = self._create_gradient(start_color, end_color)

        # Параметры шрифта
        title_font_scale = 1.8
        desc_font_scale = 0.9
        title_thickness = 3
        desc_thickness = 2
        text_color = (255, 255, 255)

        # Рисуем заголовок с тенью
        max_text_width = self.width - TemplateConfig.PADDING * 2
        title_lines = self._wrap_text(title, title_font_scale, title_thickness, max_text_width)

        y = TemplateConfig.TITLE_Y_POSITION
        for line in title_lines:
            self._put_text_with_shadow(img, line, (TemplateConfig.PADDING, y),
                                       title_font_scale, text_color, title_thickness, shadow=True)
            y += 80

        # Рисуем описание
        if description:
            y += 20
            desc_lines = self._wrap_text(description, desc_font_scale, desc_thickness, max_text_width)
            for line in desc_lines:
                self._put_text_with_shadow(img, line, (TemplateConfig.PADDING, y),
                                           desc_font_scale, text_color, desc_thickness, shadow=True)
                y += 50

        # Конвертируем в PNG и возвращаем BytesIO
        _, buffer = cv2.imencode('.png', img)
        output = BytesIO(buffer.tobytes())
        output.seek(0)
        return output

    def generate_with_background(self, title: str, description: Optional[str] = None,
                                 background_path: Optional[str] = None,
                                 background_image: Optional[np.ndarray] = None) -> BytesIO:
        """Генерация превью с пользовательским фоном"""
        # Загружаем фон
        if background_image is not None:
            img = background_image.copy()
        elif background_path and os.path.exists(background_path):
            img = cv2.imread(background_path)
            if img is None:
                # Fallback - создаем простой градиент
                return self.generate_gradient(title, description)
        else:
            # Fallback - создаем простой градиент
            return self.generate_gradient(title, description)

        # Масштабируем фон
        img = cv2.resize(img, (self.width, self.height), interpolation=cv2.INTER_LANCZOS4)

        # Добавляем полупрозрачный overlay для читаемости
        overlay = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        alpha = TemplateConfig.OVERLAY_ALPHA / 255.0
        img = cv2.addWeighted(img, 1 - alpha, overlay, alpha, 0)

        # Параметры шрифта
        title_font_scale = 1.8
        desc_font_scale = 0.9
        title_thickness = 3
        desc_thickness = 2
        text_color = (255, 255, 255)

        # Рисуем заголовок
        max_text_width = self.width - TemplateConfig.PADDING * 2
        title_lines = self._wrap_text(title, title_font_scale, title_thickness, max_text_width)

        y = TemplateConfig.TITLE_Y_POSITION
        for line in title_lines:
            self._put_text_with_shadow(img, line, (TemplateConfig.PADDING, y),
                                       title_font_scale, text_color, title_thickness, shadow=False)
            y += 80

        # Рисуем описание
        if description:
            y += 20
            desc_lines = self._wrap_text(description, desc_font_scale, desc_thickness, max_text_width)
            for line in desc_lines:
                self._put_text_with_shadow(img, line, (TemplateConfig.PADDING, y),
                                           desc_font_scale, text_color, desc_thickness, shadow=False)
                y += 50

        # Конвертируем в PNG и возвращаем BytesIO
        _, buffer = cv2.imencode('.png', img)
        output = BytesIO(buffer.tobytes())
        output.seek(0)
        return output
