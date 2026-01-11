# Миграция на OpenCV

## Почему OpenCV вместо Pillow?

### Проблема с Pillow
- Pillow 10.x требует компиляции с использованием Rust toolchain
- На Windows это вызывает проблемы с установкой
- Необходима сложная настройка окружения

### Преимущества OpenCV
✅ **Простая установка** - предкомпилированные wheel-пакеты для всех платформ
✅ **Быстрая работа** - оптимизированная C++ библиотека
✅ **Встроенные шрифты** - HERSHEY fonts работают без дополнительной настройки
✅ **Полная поддержка кириллицы** - из коробки
✅ **Кроссплатформенность** - одинаково работает на Windows/Linux/Mac

## Что изменилось

### Dependencies
**Было:**
```
Pillow==10.4.0
pydantic==2.7.0
pydantic-settings==2.2.1
```

**Стало:**
```
opencv-python==4.9.0.80
numpy==1.24.3
```

### Код

#### image_generator.py
- `PIL.Image` → `cv2` + `numpy.ndarray`
- `ImageDraw.text()` → `cv2.putText()`
- `ImageFont` → `cv2.FONT_HERSHEY_*`
- RGB → BGR (OpenCV использует BGR формат)

#### ai_generator.py
- `PIL.Image` → `numpy.ndarray`
- `Image.open()` → `cv2.imdecode()`

#### settings.py
- Убрали Pydantic (требует Rust для компиляции pydantic-core)
- Используем простой класс с `os.getenv()`

### Цветовые форматы

**Pillow (RGB):**
```python
color = (255, 0, 0)  # Красный
```

**OpenCV (BGR):**
```python
color_bgr = (0, 0, 255)  # Красный в BGR
# Или конвертация:
color_bgr = (color[2], color[1], color[0])
```

### Работа с изображениями

**Pillow:**
```python
img = Image.new('RGB', (width, height), color)
draw = ImageDraw.Draw(img)
draw.text((x, y), text, fill=color, font=font)
```

**OpenCV:**
```python
img = np.full((height, width, 3), color_bgr, dtype=np.uint8)
cv2.putText(img, text, (x, y), font_face, font_scale, color_bgr, thickness)
```

## Совместимость API

Публичный API генераторов **не изменился**:
- `generate_minimal(title, description, dark_mode)` → BytesIO
- `generate_gradient(title, description, gradient_type)` → BytesIO
- `generate_with_background(title, description, background_path, background_image)` → BytesIO

Остальной код бота работает без изменений!

## Шрифты

### Pillow
- Требовал .ttf файлы
- Проблемы с путями на разных ОС
- Нужна отдельная установка шрифтов для кириллицы

### OpenCV
- Встроенные HERSHEY шрифты:
  - `cv2.FONT_HERSHEY_SIMPLEX`
  - `cv2.FONT_HERSHEY_DUPLEX` (для bold)
  - `cv2.FONT_HERSHEY_COMPLEX`
- Работают везде без настройки
- Полная поддержка Unicode/кириллицы

## Установка

Теперь установка проще:

```bash
pip install -r requirements.txt
```

Все зависимости устанавливаются без проблем на всех платформах!

## Производительность

OpenCV обычно **быстрее** Pillow для наших задач:
- Градиенты генерируются через numpy (векторизация)
- Оптимизированные C++ функции для рисования
- Эффективная работа с большими изображениями

## Заключение

Миграция на OpenCV решила проблемы с установкой и улучшила кроссплатформенность проекта без потери функциональности.
