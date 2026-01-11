# Структура проекта

```
imgpreviewgen/
│
├── main.py                      # Точка входа, запуск бота
│
├── config/                      # Конфигурация
│   ├── __init__.py
│   └── settings.py             # Pydantic настройки, загрузка .env
│
├── bot/                        # Telegram бот
│   ├── __init__.py
│   ├── handlers.py            # Обработчики команд и сообщений
│   ├── keyboards.py           # Inline клавиатуры
│   └── states.py              # Константы состояний ConversationHandler
│
├── generator/                  # Генерация изображений
│   ├── __init__.py
│   ├── image_generator.py     # Pillow: минимализм, градиенты, свой фон
│   ├── ai_generator.py        # AI-генерация через vsellm.ru
│   └── templates.py           # Цветовые схемы, размеры, конфиги
│
├── assets/                     # Ресурсы
│   ├── fonts/                 # Пользовательские шрифты (.ttf)
│   │   └── README.md
│   └── backgrounds/           # Предустановленные фоны (не используется)
│       └── README.md
│
├── temp/                       # Временные файлы (создается автоматически)
│
├── .env                        # Переменные окружения (создать вручную)
├── .env.example               # Пример .env файла
├── .gitignore                 # Git ignore правила
│
├── requirements.txt           # Python зависимости
│
├── README.md                  # Основная документация
├── QUICKSTART.md             # Быстрый старт
├── ARCHITECTURE.md           # Техническая архитектура
├── CONCEPT.md                # Концепт проекта
├── CLAUDE.md                 # Руководство для Claude Code
└── PROJECT_STRUCTURE.md      # Этот файл
```

## Описание ключевых файлов

### main.py
- Инициализация бота
- Регистрация обработчиков
- Настройка ConversationHandler
- Создание необходимых директорий

### config/settings.py
- Класс Settings с Pydantic
- Автоматическая загрузка из .env
- Валидация типов и значения по умолчанию

### bot/handlers.py
- Все callback функции для команд
- Логика conversation flow
- Обработка пользовательского ввода
- Вызов генераторов изображений

### generator/image_generator.py
- Класс ImageGenerator
- 3 основных метода:
  - `generate_minimal()` - минималистичный стиль
  - `generate_gradient()` - градиентный фон
  - `generate_with_background()` - пользовательский/AI фон
- Вспомогательные методы для текста и шрифтов

### generator/ai_generator.py
- Класс AIImageGenerator
- Интеграция с vsellm.ru API
- OpenAI-совместимый формат запросов
- Создание промптов из заголовков

## Потоки данных

### Создание превью (упрощенно)

```
Пользователь -> /new
            ↓
    Выбор стиля (keyboards.py)
            ↓
    Ввод заголовка (handlers.py)
            ↓
    Ввод описания (handlers.py)
            ↓
    Генерация (image_generator.py или ai_generator.py)
            ↓
    Отправка фото пользователю
```

### ConversationHandler States

```
START
  ↓
CHOOSING_STYLE → [gradient?] → CHOOSING_STYLE (выбор цвета)
  ↓                             ↓
  ↓ [custom bg?] → UPLOADING_CUSTOM_BG
  ↓                             ↓
ENTERING_TITLE ←←←←←←←←←←←←←←←←←
  ↓
ENTERING_DESCRIPTION
  ↓
Генерация и отправка
  ↓
END
```

## Зависимости между модулями

```
main.py
  ├─→ config.settings (глобальные настройки)
  ├─→ bot.handlers (все обработчики)
  └─→ bot.states (константы состояний)

bot/handlers.py
  ├─→ bot.keyboards (клавиатуры)
  ├─→ bot.states (состояния)
  ├─→ generator.image_generator (Pillow генерация)
  ├─→ generator.ai_generator (AI генерация)
  └─→ config.settings (настройки)

generator/image_generator.py
  └─→ generator.templates (цвета, размеры)

generator/ai_generator.py
  └─→ config.settings (API ключи)
```

## Файлы конфигурации

- `.env` - секреты и настройки (не в Git)
- `requirements.txt` - Python зависимости
- `.gitignore` - правила игнорирования

## Временные файлы

- `temp/bg_{user_id}.jpg` - загруженные пользователями фоны
- Автоматически удаляются после генерации
