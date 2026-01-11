"""Проверка доступных моделей на vsellm.ru"""
# -*- coding: utf-8 -*-

import os
import sys
import requests
from dotenv import load_dotenv

# Устанавливаем UTF-8 для Windows консоли
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

api_key = os.getenv('VSELLM_API_KEY')
api_url = os.getenv('VSELLM_API_URL', 'https://api.vsellm.ru/v1')

print("="*50)
print("ДОСТУПНЫЕ МОДЕЛИ НА VSELLM.RU")
print("="*50)

if not api_key or api_key.startswith('__n8n_BLANK_VALUE'):
    print("[X] API ключ не настроен!")
    exit(1)

try:
    # Получаем список моделей
    response = requests.get(
        f"{api_url}/models",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        timeout=10
    )

    print(f"\nStatus Code: {response.status_code}\n")

    if response.status_code == 200:
        data = response.json()

        print("Доступные модели для генерации изображений:\n")

        image_models = []
        if 'data' in data:
            for model in data['data']:
                model_id = model.get('id', '')
                # Ищем модели для генерации изображений
                if any(keyword in model_id.lower() for keyword in ['dall', 'image', 'stable', 'midjourney', 'kandinsky', 'gemini', 'imagen', 'vertex']):
                    image_models.append(model)

                    # Выводим информацию о модели
                    print(f"  [{len(image_models)}] {model_id}")

                    # Выводим все доступные поля модели
                    model_info = []
                    if 'owned_by' in model:
                        model_info.append(f"Владелец: {model['owned_by']}")
                    if 'max_tokens' in model:
                        model_info.append(f"Max tokens: {model['max_tokens']}")
                    if 'context_length' in model:
                        model_info.append(f"Context: {model['context_length']}")
                    if 'context_window' in model:
                        model_info.append(f"Context window: {model['context_window']}")
                    if 'max_input_tokens' in model:
                        model_info.append(f"Max input: {model['max_input_tokens']}")
                    if 'max_output_tokens' in model:
                        model_info.append(f"Max output: {model['max_output_tokens']}")

                    if model_info:
                        for info in model_info:
                            print(f"      {info}")

        if not image_models:
            print("  [!] Модели для генерации изображений не найдены")
            print("\n  Все доступные модели:")
            if 'data' in data:
                for model in data['data'][:20]:  # Показываем первые 20
                    print(f"  - {model.get('id', 'unknown')}")

        print(f"\n[OK] Найдено {len(image_models)} моделей для изображений")

        # Пытаемся получить информацию о балансе через разные эндпоинты
        print("\n" + "="*50)
        print("ПРОВЕРКА БАЛАНСА И ЛИМИТОВ")
        print("="*50)

        # Вариант 1: /dashboard/billing/subscription
        balance_found = False
        try:
            balance_response = requests.get(
                f"{api_url}/dashboard/billing/subscription",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            if balance_response.status_code == 200:
                balance_info = balance_response.json()
                if balance_info:
                    print("\n[OK] Информация о подписке:")
                    print(f"  {balance_info}")
                    balance_found = True
        except Exception as e:
            pass

        # Вариант 2: /dashboard/billing/credit_grants
        if not balance_found:
            try:
                credit_response = requests.get(
                    f"{api_url}/dashboard/billing/credit_grants",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10
                )
                if credit_response.status_code == 200:
                    credit_info = credit_response.json()
                    if credit_info:
                        print("\n[OK] Информация о кредитах:")
                        print(f"  {credit_info}")
                        balance_found = True
            except Exception:
                pass

        # Вариант 3: /usage
        if not balance_found:
            try:
                usage_response = requests.get(
                    f"{api_url}/usage",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10
                )
                if usage_response.status_code == 200:
                    usage_info = usage_response.json()
                    if usage_info:
                        print("\n[OK] Информация об использовании:")
                        print(f"  {usage_info}")
                        balance_found = True
            except Exception:
                pass

        if not balance_found:
            print("\n[!] API vsellm.ru не предоставляет информацию о балансе через публичные эндпоинты")
            print("    Проверьте баланс в личном кабинете: https://vsellm.ru/dashboard")

        if image_models:
            print(f"\n[!] Рекомендуемая модель для использования: {image_models[0].get('id', 'N/A')}")
    else:
        print(f"[X] Ошибка: {response.status_code}")
        print(f"Ответ: {response.text[:500]}")

except Exception as e:
    print(f"[X] Ошибка: {e}")

print("\n" + "="*50)
