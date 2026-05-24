import json
import requests
from abc import ABC, abstractmethod
import logging
from .models import EventData


class LLMProvider(ABC):
    @abstractmethod
    def parse(self, text: str, schema: dict) -> dict:
        pass

    def _build_prompt(self, schema: dict) -> str:
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
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def parse(self, text: str, schema: dict) -> dict:
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

        response = requests.post(self.url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return json.loads(data["choices"][0]["message"]["content"])


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def parse(self, text: str, schema: dict) -> dict:
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

        response = requests.post(self.url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return json.loads(data["choices"][0]["message"]["content"])


class FallbackLLMParser:
    def __init__(self, providers: list[LLMProvider]):
        self.providers = providers

    def parse(self, text: str):
        if not text.strip():
            return None

        schema = EventData.model_json_schema()
        last_error = None

        for provider in self.providers:
            try:
                return provider.parse(text, schema)
            except Exception as e:
                last_error = e
                logging.error("Ошибка у {provider.__class__.__name__}: {e}")

        logging.error("Все API недоступны. Последняя ошибка: {last_error}")
        return None
