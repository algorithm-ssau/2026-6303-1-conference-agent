# import requests
import aiohttp
from typing import Optional, Dict


class PostService:
    """
      Сервис генерации постов через LLM (DeepSeek).
    """
    def __init__(self, api_key: str):
      self.api_key = api_key
      self.url = "https://api.deepseek.com/v1/chat/completions"
      self.headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
      }

    async def generate_post(
        self,
        text: str,
        template: str = "default",
        tone: str = "professional",
        max_length: int = 500,
        language: str = "ru"
    ) -> Optional[str]:
        """
        Генерирует текст поста на основе входного текста.

        :param text: Исходный текст (например, описание конференции)
        :param template: Тип поста (default/social)
        :param tone: Тон текста
        :param max_length: Ограничение длины
        :param language: Язык
        :return: Сгенерированный пост или None
        """
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
          async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
          
              response.raise_for_status()
              
              if response.status_code != 200:
                print(f"DeepSeek API error: {response.status_code}")
                return None
              
              data = await response.json()
              return data["choices"][0]["message"]["content"]


        except Exception as e:
          print(f"Ошибка генерации поста: {e}")
          return None