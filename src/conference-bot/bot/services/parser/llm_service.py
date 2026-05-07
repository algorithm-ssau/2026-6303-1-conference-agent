import json
# import requests
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
  def __init__(self, api_key: str, model: str):
    self.api_key = api_key
    self.model = model
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
    payload = {
      "model": self.model,
      "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Текст для анализа: \n{text}"}
      ],
      "response_format": {"type": "json_object"},
      "temperature": 0.1
    }
    async with aiohttp.ClientSession() as session:
      async with session.post(
          self.url,
          headers=headers,
          json=payload,
          timeout=aiohttp.ClientTimeout(total=60)
      ) as response:

          response.raise_for_status()

          data = await response.json()

          return json.loads(
              data["choices"][0]["message"]["content"]
          )

    # response = requests.post(
    #   self.url, 
    #   headers=headers, 
    #   json=payload, 
    #   timeout=60
    
    # )
    # response.raise_for_status()
    # data = response.json()
    
    # return json.loads(data["choices"][0]["message"]["content"])


class GroqProvider(LLMProvider):
  """
    Реализация LLM через Groq API.
  """
  def __init__(self, api_key: str, model: str):
    self.api_key = api_key
    self.model = model
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
    payload = {
      "model": self.model,
      "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Текст для анализа: \n{text}"}
      ],
      "response_format": {"type": "json_object"},
      "temperature": 0.1
    }

    # response = aiohttp.post(self.url, headers=headers, json=payload, timeout=60)
    # response.raise_for_status()
    # data = response.json()
    # return json.loads(data["choices"][0]["message"]["content"])
    async with aiohttp.ClientSession() as session:
      async with session.post(
        self.url,
        headers=headers,
        json=payload,
        timeout=aiohttp.ClientTimeout(total=60)
      ) as response:

        response.raise_for_status()

        data = await response.json()

        return json.loads(
          data["choices"][0]["message"]["content"]
        )


class FallbackLLMParser:
  """
    Последовательно пробует несколько LLM-провайдеров.
    Используется как fallback-механизм.
  """
  def __init__(self, providers: list[LLMProvider]):
    self.providers = providers

  async def parse(self, text: str):
    """
      Пытается распарсить текст через список провайдеров.

      :param text: Входной текст
      :return: dict с данными или None
    """
    if not text.strip():
      return None

    schema = EventData.model_json_schema()
    last_error = None

    for provider in self.providers:
      try:
        return await provider.parse(text, schema)
      except Exception as e:
        last_error = e
        logging.error("Ошибка у {provider.__class__.__name__}: {e}")

    logging.error("Все API недоступны. Последняя ошибка: {last_error}")
    return None
