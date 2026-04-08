import requests
import json
from typing import List, Dict, Optional


class DeepSeekBot:
    def __init__(self, api_key: str):
        """
        Инициализация бота с API ключом

        Args:
            api_key: Ваш API ключ DeepSeek
        """
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.conversation_history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """
        Добавление сообщения в историю

        Args:
            role: "user" или "assistant"
            content: текст сообщения
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def clear_history(self):
        """Очистка истории диалога"""
        self.conversation_history = []

    def send_message(self, message: str, temperature: float = 0.7,
                     max_tokens: int = 2000) -> Optional[str]:
        """
        Отправка сообщения и получение ответа

        Args:
            message: текст сообщения
            temperature: креативность ответа (0-1)
            max_tokens: максимальная длина ответа

        Returns:
            ответ ассистента или None в случае ошибки
        """
        # Добавляем сообщение пользователя в историю
        self.add_message("user", message)

        # Подготовка запроса
        payload = {
            "model": "deepseek-chat",
            "messages": self.conversation_history,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            # Отправка запроса к API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            # Проверка ответа
            if response.status_code == 200:
                assistant_response = response.json()["choices"][0]["message"]["content"]
                # Сохраняем ответ ассистента в историю
                self.add_message("assistant", assistant_response)
                return assistant_response
            else:
                print(f"Ошибка API: {response.status_code}")
                print(response.text)
                return None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга ответа: {e}")
            return None

    def send_message_without_history(self, message: str, **kwargs) -> Optional[str]:
        """
        Отправка сообщения без сохранения в истории

        Args:
            message: текст сообщения

        Returns:
            ответ ассистента или None в случае ошибки
        """
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": message}],
            **kwargs
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"Ошибка API: {response.status_code}")
                return None

        except Exception as e:
            print(f"Ошибка: {e}")
            return None


def create_post_from_text(
        api_key: str,
        text: str,
        template: str = "default",
        tone: str = "professional",
        max_length: int = 500,
        language: str = "ru",
        additional_instructions: Optional[str] = None
) -> Optional[Dict]:
    """
    Функция для создания поста из текста по шаблону

    Args:
        api_key: API ключ DeepSeek
        text: исходный текст
        template: шаблон поста ("default", "social", "blog", "news", "teaser")
        tone: тон поста ("professional", "casual", "enthusiastic", "educational")
        max_length: максимальная длина поста
        language: язык поста ("ru", "en")
        additional_instructions: дополнительные инструкции

    Returns:
        словарь с результатом или None в случае ошибки
    """

    # Шаблоны промптов
    templates = {
        "default": """
Создай пост на основе предоставленного текста.

Текст:
{text}

Требования к посту:
- Язык: {language}
- Тон: {tone}
- Максимальная длина: {max_length} символов
- Структура: заголовок + основной текст
- Выдели ключевые идеи текста
- Сделай пост интересным и вовлекающим
""",

        "social": """
Создай пост для социальных сетей на основе текста.

Текст:
{text}

Требования к посту:
- Язык: {language}
- Тон: {tone}
- Максимальная длина: {max_length} символов
- Добавь эмодзи для эмоциональной окраски
- Используй хэштеги в конце (3-5 шт)
- Сделай первый абзац цепляющим
- Формат: кратко, ярко, вовлекающе
""",

        "blog": """
Создай пост для блога на основе текста.

Текст:
{text}

Требования к посту:
- Язык: {language}
- Тон: {tone}
- Максимальная длина: {max_length} символов
- Структура: заголовок, введение, основная часть, вывод
- Добавь подзаголовки для структурирования
- Используй примеры и аналогии
- Сделай пост полезным и экспертным
""",

        "news": """
Создай новостной пост на основе текста.

Текст:
{text}

Требования к посту:
- Язык: {language}
- Тон: {tone}
- Максимальная длина: {max_length} символов
- Формат: кто, что, где, когда, почему
- Выдели главную новость в начале
- Добавь цитаты или ключевые цифры
- Сделай акцент на важности события
""",

        "teaser": """
Создай тизер-пост на основе текста.

Текст:
{text}

Требования к посту:
- Язык: {language}
- Тон: {tone}
- Максимальная длина: {max_length} символов
- Создай интригующий заголовок
- Раскрой проблему, но не давай полное решение
- Добавь вопрос в конце для вовлечения
- Используй короткие, энергичные предложения
"""
    }

    # Выбираем шаблон
    selected_template = templates.get(template, templates["default"])

    # Формируем промпт
    prompt = selected_template.format(
        text=text[:3000],  # Ограничиваем длину текста
        language="Русский" if language == "ru" else "English",
        tone=tone,
        max_length=max_length
    )

    # Добавляем дополнительные инструкции
    if additional_instructions:
        prompt += f"\n\nДополнительные требования:\n{additional_instructions}"

    # Подготовка запроса к API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "Ты профессиональный копирайтер и контент-менеджер. Твоя задача - создавать качественные посты из текста, следуя всем требованиям."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": max_length * 2  # Запас для кириллицы
    }

    try:
        # Отправляем запрос
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            post_content = result["choices"][0]["message"]["content"]

            return {
                "success": True,
                "post": post_content,
                "template_used": template,
                "length": len(post_content)
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}",
                "details": response.text
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def create_posts_batch(
        api_key: str,
        texts: List[str],
        template: str = "social",
        **kwargs
) -> List[Dict]:
    """
    Создание постов из нескольких текстов

    Args:
        api_key: API ключ
        texts: список текстов
        template: шаблон для всех постов
        **kwargs: дополнительные параметры для create_post_from_text

    Returns:
        список результатов
    """
    results = []

    for i, text in enumerate(texts):
        print(f"Обработка текста {i + 1}/{len(texts)}...")
        result = create_post_from_text(
            api_key=api_key,
            text=text,
            template=template,
            **kwargs
        )
        results.append(result)

    return results


class TextToPostConverter:
    """Класс для конвертации текста в посты"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.templates = ["default", "social", "blog", "news", "teaser"]

    def convert(self, text: str, template: str = "social", **kwargs) -> Optional[str]:
        """
        Конвертация текста в пост

        Args:
            text: исходный текст
            template: шаблон поста
            **kwargs: дополнительные параметры

        Returns:
            текст поста или None
        """
        result = create_post_from_text(
            api_key=self.api_key,
            text=text,
            template=template,
            **kwargs
        )

        return result["post"] if result and result["success"] else None

    def compare_templates(self, text: str, **kwargs) -> Dict[str, Optional[str]]:
        """
        Сравнение всех шаблонов для одного текста

        Args:
            text: исходный текст
            **kwargs: параметры для create_post_from_text

        Returns:
            словарь с результатами для каждого шаблона
        """
        results = {}

        for template in self.templates:
            print(f"Генерация для шаблона '{template}'...")
            results[template] = self.convert(text, template, **kwargs)

        return results


# Пример использования
def main():
    # Замените на ваш реальный API ключ
    API_KEY = "your-api-key-here"

    # Создаем экземпляр бота
    bot = DeepSeekBot(API_KEY)

    print("Бот DeepSeek запущен! Введите 'exit' для выхода, 'clear' для очистки истории.")
    print("Введите 'post' для создания поста из текста.")
    print("-" * 50)

    while True:
        user_input = input("\nВы: ").strip()

        if user_input.lower() == 'exit':
            print("До свидания!")
            break
        elif user_input.lower() == 'clear':
            bot.clear_history()
            print("История диалога очищена!")
            continue
        elif user_input.lower() == 'post':
            print("\nВведите текст для создания поста:")
            text = input("Текст: ").strip()

            if text:
                print("\nВыберите шаблон (default/social/blog/news/teaser):")
                template = input("Шаблон (по умолчанию social): ").strip() or "social"

                result = create_post_from_text(
                    api_key=API_KEY,
                    text=text,
                    template=template,
                    max_length=500
                )

                if result and result["success"]:
                    print(f"\n=== Созданный пост ===\n{result['post']}")
                    print(f"\nДлина: {result['length']} символов")
                else:
                    print(f"\nОшибка: {result['error'] if result else 'Неизвестная ошибка'}")
            continue
        elif not user_input:
            continue

        # Получаем ответ от бота
        response = bot.send_message(user_input)

        if response:
            print(f"\nБот: {response}")
        else:
            print("\nБот: Извините, произошла ошибка. Попробуйте позже.")


if __name__ == "__main__":
    main()