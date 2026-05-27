import aiohttp
from typing import Optional, Dict
from bot.config import OPENROUTER_API_KEY, OPENROUTER_MODELS, GROQ_MODELS

class PostService:
    """
      Сервис генерации постов через LLM (DeepSeek).
    """
    def __init__(self):
      self.api_key = OPENROUTER_API_KEY  # Берем ключ из config.py
      self.url = "https://openrouter.ai/api/v1/chat/completions"
      self.headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
      }
      self.models = OPENROUTER_MODELS

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
ВАЖНО: Используй ТОЛЬКО HTML-теги для форматирования (<b>жирный</b>, <i>курсив</i>, <u>подчёркнутый</u>). Разметка Markdown (**) СТРОГО ЗАПРЕЩЕНА!
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

Используй HTML-теги для форматирования (<b>жирный</b>, <i>курсив</i>, <u>подчёркнутый</u>). Разметка Markdown (**) запрещена.
"""
        }

        prompt = templates.get(template, templates["default"]).format(
          text=text[:3000],
          language="Русский" if language == "ru" else "English",
          tone=tone,
          max_length=max_length
        )

        for model in self.models:
          payload = {
            "model": model,
            "messages": [
              {
                "role": "system",
                "content": "Ты пишешь посты о научных конференциях. Используй строго HTML-разметку, без Markdown."
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
            print(f"➡ Пробую модель: {model}")

            async with aiohttp.ClientSession() as session:
              async with session.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
              ) as response:

                if response.status != 200:
                  print(f"❌ {model} вернула {response.status}")
                  continue

                data = await response.json()

                try:
                  content = data["choices"][0]["message"]["content"]
                  print(f"✅ Успех на модели: {model}")
                  return content
                except (KeyError, IndexError):
                  print(f"❌ Кривой ответ от {model}: {data}")
                  continue

          except Exception as e:
            print(f"❌ Ошибка на модели {model}: {e}")
            continue

        print("💀 Все модели умерли")
        return None
    

    async def generate_tags(self, text: str, max_tags: int = 7, exclude_tags: list[str] = None) -> list[str]:
      prompt = f"Сгенерируй {max_tags} подходящих хэштегов для текста. Выведи только хэштеги через пробел, без нумерации и лишних слов.\n\nТекст: {text[:2000]}"
      
      # Передаем список запрещенных тегов
      if exclude_tags:
        prompt += f"СТРОГО ЗАПРЕЩЕНО использовать следующие хэштеги: {', '.join(exclude_tags)}\n"

      prompt += f"\nТекст: {text[:2000]}"
      for model in self.models:
        payload = {
          "model": model,
          "messages": [{"role": "user", "content": prompt}],
          "temperature": 0.3,
        }
        try:
          async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=self.headers, json=payload, timeout=30) as response:
              if response.status == 200:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                # Очищаем ответ от лишних символов и добавляем '#'
                tags = [t if t.startswith("#") else f"#{t}" for t in content.split() if t]
                return tags[:max_tags]
        except Exception as e:
          print(f"Ошибка при генерации тегов: {e}")
          continue
      return []
