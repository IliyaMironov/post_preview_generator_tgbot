# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Telegram bot for generating preview images for blog posts. Uses Python with python-telegram-bot library for bot functionality and Pillow for image generation. Optionally integrates with vsellm.ru API for AI-generated illustrations.

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
# Then edit .env with your tokens
```

### Running the Bot
```bash
python main.py
```

### Testing Locally
To test bot functionality:
1. Set `TELEGRAM_BOT_TOKEN` in `.env` (get from @BotFather)
2. Run `python main.py`
3. Find your bot on Telegram and send `/start`

## Architecture

### Core Components

**Bot Layer** (`bot/`):
- `handlers.py` - All command and message handlers, including conversation flow logic
- `keyboards.py` - Inline keyboard layouts for user interactions
- `states.py` - ConversationHandler state constants

**Generator Layer** (`generator/`):
- `image_generator.py` - Core image generation using OpenCV (minimal, gradient, custom background styles)
- `ai_generator.py` - Optional AI illustration generation via vsellm.ru API
- `templates.py` - Color schemes, size constants, and template configurations

**Configuration** (`config/`):
- `settings.py` - Pydantic-based settings management, loads from `.env`

### Conversation Flow

The bot uses `ConversationHandler` with these states:
1. `CHOOSING_STYLE` - User selects design style (minimal/gradient/AI/custom)
2. `UPLOADING_CUSTOM_BG` - Optional: user uploads custom background image
3. `ENTERING_TITLE` - User enters post title
4. `ENTERING_DESCRIPTION` - User enters post description (optional)

After description (or skip), image is generated and sent to user.

### Image Generation Approaches

**1. Minimal Style** (`generate_minimal`):
- Solid background (light/dark mode)
- Accent line on the left
- Clean sans-serif typography
- Text wrapping for long titles

**2. Gradient Style** (`generate_gradient`):
- Vertical gradient between two colors
- 6 predefined color schemes (sunset, ocean, pink, forest, night, fire)
- White text with shadow for readability
- Defined in `templates.py` `ColorScheme` class

**3. Custom Background** (`generate_with_background`):
- User uploads their own image
- Image is resized/cropped to 1280x640
- Semi-transparent black overlay (alpha=180) for text readability

**4. AI Style** (optional):
- Uses vsellm.ru OpenAI-compatible API (`/v1/images/generations`)
- Generates illustration based on post title
- Falls back to gradient if API unavailable or fails

### Text Handling

All generators use `_wrap_text()` method that:
- Splits text into words
- Measures line width with `cv2.getTextSize()`
- Breaks into multiple lines when exceeding max width
- Returns list of lines for rendering

Font system:
- OpenCV uses built-in HERSHEY fonts (cv2.FONT_HERSHEY_DUPLEX for bold)
- No external font files needed - works cross-platform
- Supports all Unicode characters including Cyrillic

## Configuration

All settings managed via Pydantic in `config/settings.py`:
- Loads from `.env` file
- Type validation and defaults
- Accessed globally via `from config import settings`

Key settings:
- `telegram_bot_token` - Required
- `vsellm_api_key` - Optional (for AI generation)
- Image dimensions: 1280x640 (optimal for Telegram)
- Font sizes: 72px title, 36px description
- Padding: 60px from edges

## vsellm.ru API Integration

API endpoint: `https://api.vsellm.ru/v1/images/generations`

Compatible with OpenAI format:
```python
POST /v1/images/generations
Headers: Authorization: Bearer {api_key}
Body: {
    "prompt": "description",
    "n": 1,
    "size": "1024x1024"
}
```

Returns URL to generated image, which is downloaded and passed to `generate_with_background()`.

## File Structure Notes

- `temp/` - Stores temporary user-uploaded backgrounds, cleaned after generation
- `assets/fonts/` - Optional custom font files
- `assets/backgrounds/` - Currently unused, reserved for preset backgrounds
- All directories auto-created on startup in `main.py`

## Adding New Features

**New gradient color scheme:**
1. Add color tuple to `ColorScheme` class in `generator/templates.py`
2. Add mapping in `get_gradient_colors()` function
3. Add button in `get_gradient_colors_keyboard()` in `bot/keyboards.py`
4. Add display name in `get_gradient_name()` in `bot/handlers.py`

**New style:**
1. Create generation method in `ImageGenerator` class
2. Add style option in `get_style_keyboard()`
3. Add handling in `style_chosen()` callback
4. Add generation logic in `generate_and_send()`

## Dependencies

- `python-telegram-bot==20.7` - Telegram Bot API wrapper
- `opencv-python==4.9.0.80` - Image manipulation and generation
- `numpy==1.24.3` - Array operations for OpenCV
- `requests==2.31.0` - HTTP client for vsellm.ru
- `python-dotenv==1.0.0` - Environment variables
