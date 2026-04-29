import requests
from typing import Optional, Dict


class PostService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def generate_post(
        self,
        text: str,
        template: str = "default",
        tone: str = "professional",
        max_length: int = 500,
        language: str = "ru"
    ) -> Optional[str]:
        """Генерация поста из текста"""

        templates = {
            "default": """
Создай пост на основе текста.

Текст:
{text}

Требования:
- Язык: {language}
- Тон: {tone}
- До {max_length} символов
- Формат: заголовок + текст
""",

            "social": """
Создай пост для соцсетей.

Текст:
{text}

Требования:
- Язык: {language}
- Тон: {tone}
- До {max_length} символов
- Добавь эмодзи
- Добавь 3-5 хэштегов
"""
        }

        prompt = templates.get(template, templates["default"]).format(
            text=text[:3000],
            language="Русский" if language == "ru" else "English",
            tone=tone,
            max_length=max_length
        )

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты пишешь краткие и понятные посты о научных конференциях."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": max_length * 2
        }

        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                print(f"DeepSeek API error: {response.status_code}")
                return None

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"Ошибка генерации поста: {e}")
            return None