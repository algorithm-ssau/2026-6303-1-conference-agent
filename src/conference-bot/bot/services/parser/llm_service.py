import json
import aiohttp
from abc import ABC, abstractmethod
import logging
from .models import EventData


class LLMProvider(ABC):
  """
    Абстрактный класс для провайдеров LLM.
    Определяет интерфейс метода parse().
  """
  @abstractmethod
  async def parse(self, text: str, schema: dict) -> dict:
    '''
      Должен быть реализован в наследниках.
      Выполняет парсинг текста в структуру по schema.
    '''
    pass

  def _build_prompt(self, schema: dict) -> str:
    """
      Формирует системный промпт для LLM.

      :param schema: JSON-схема результата
      :return: Строка промпта
    """
    return f"""
Ты эксперт по анализу документов. Твоя задача — извлечь данные о мероприятии.
ПРАВИЛА:
1. Для дат (deadlines) всегда пиши понятное описание на русском языке.
2. Для ссылок (links) всегда пиши, что это за ресурс.
3. Для направлений (topics): найди все секции, научные направления или темы.
4. Если данных нет, используй null.
Верни JSON по схеме:
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


class OpenRouterProvider(LLMProvider):
  """
    Реализация LLM через OpenRouter API.
  """
  def __init__(self, api_key: str, models: list[str]):
    self.api_key = api_key
    self.models = models
    self.url = "https://openrouter.ai/api/v1/chat/completions"

  async def parse(self, text: str, schema: dict) -> dict:
    """
    Отправляет текст в OpenRouter и получает структурированный JSON.

    :return: dict с данными события
    """
    system_prompt = self._build_prompt(schema)
    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }
    for model in self.models:
      payload = {
        "model": model,
        "messages": [
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": f"Текст:\n{text}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
      }

      try:
        logging.info(f"➡ OpenRouter: пробую {model}")

        # В llm_service.py, перед отправкой запроса:
        logging.info(f"📤 Отправляю в LLM текст длиной: {len(text)} символов")
        logging.debug(f"📄 Первые 500 символов текста:\n{text[:500]}")

        async with aiohttp.ClientSession() as session:
          async with session.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
          ) as response:

              if response.status != 200:
                text = await response.text()
                logging.error(f"""
            ❌ API ERROR
            Provider: OpenRouter
            Model: {model}
            Status: {response.status}
            Response: {text[:500]}
            """)
                continue

              data = await response.json()

              try:
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                logging.debug(f"RAW LLM RESPONSE: {content[:1000]}")
                return parsed
              except Exception:
                logging.error(f"{model} вернул кривой JSON")
                continue

      except Exception as e:
        logging.error(f"{model} упал: {e}")
        continue

    return None


class GroqProvider(LLMProvider):
  """
    Реализация LLM через Groq API.
  """
  def __init__(self, api_key: str, models: list[str]):
    self.api_key = api_key
    self.models = models
    self.url = "https://api.groq.com/openai/v1/chat/completions"

  async def parse(self, text: str, schema: dict) -> dict:
    """
      Аналогично OpenRouter, но через Groq API.
    """
    system_prompt = self._build_prompt(schema)
    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json; charset=utf-8"
    }
    for model in self.models:
      payload = {
        "model": model,
        "messages": [
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": f"Текст:\n{text}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
      }

      try:
        logging.info(f"➡ Groq: пробую {model}")

        async with aiohttp.ClientSession() as session:
          async with session.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
          ) as response:
              if response.status != 200:
                if response.status != 200:
                  text = await response.text()
                  logging.error(f"""
              ❌ API ERROR
              Provider: OpenRouter
              Model: {model}
              Status: {response.status}
              Response: {text[:500]}
              """)
                  continue

              data = await response.json()

              try:
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                logging.debug(f"RAW LLM RESPONSE: {content[:1000]}")
                return parsed
              except Exception:
                logging.error(f"{model} вернул кривой JSON")
                continue

      except Exception as e:
        logging.error(f"{model} упал: {e}")
        continue

    return None


class FallbackLLMParser:
  """
    Последовательно пробует несколько LLM-провайдеров.
    Используется как fallback-механизм.
  """
  def __init__(self, providers: list[LLMProvider], retries: int = 2):
    self.providers = providers
    self.retries = retries

  async def parse(self, text: str):
    """
      Пытается распарсить текст через список провайдеров.

      :param text: Входной текст
      :return: dict с данными или None
    """
    if not text.strip():
      return None

    schema = EventData.model_json_schema()

    
    for attempt in range(self.retries):
      logging.info(f"🔁 Попытка {attempt + 1}")

      for provider in self.providers:
        try:
          result = await provider.parse(text, schema)

          if result:
            logging.info(f"✅ Успех: {provider.__class__.__name__}")
            return result
          if result is None:
            logging.warning(f"{provider.__class__.__name__} не дал результат")

        except Exception as e:
          logging.error(f"{provider.__class__.__name__} ошибка: {e}")

    logging.error("💀 Все провайдеры умерли")
    return None