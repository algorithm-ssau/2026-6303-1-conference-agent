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


import requests
import json
from typing import Optional, Dict, List


def create_post_from_document(
        api_key: str,
        document_text: str,
        template: str = "default",
        tone: str = "professional",
        max_length: int = 500,
        language: str = "ru",
        additional_instructions: Optional[str] = None
) -> Optional[Dict]:
    """
    Функция для создания поста из документа по шаблону

    Args:
        api_key: API ключ DeepSeek
        document_text: текст документа
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
Создай пост на основе предоставленного документа.

Документ:
{document}

Требования к посту:
- Язык: {language}
- Тон: {tone}
- Максимальная длина: {max_length} символов
- Структура: заголовок + основной текст
- Выдели ключевые идеи документа
- Сделай пост интересным и вовлекающим
""",

        "social": """
Создай пост для социальных сетей на основе документа.

Документ:
{document}

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
Создай пост для блога на основе документа.

Документ:
{document}

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
Создай новостной пост на основе документа.

Документ:
{document}

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
Создай тизер-пост на основе документа.

Документ:
{document}

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
        document=document_text[:3000],  # Ограничиваем длину документа
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
                "content": "Ты профессиональный копирайтер и контент-менеджер. Твоя задача - создавать качественные посты из документов, следуя всем требованиям."
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

            # Парсим результат (можно улучшить в зависимости от формата)
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


def create_post_batch(
        api_key: str,
        documents: List[str],
        template: str = "social",
        **kwargs
) -> List[Dict]:
    """
    Создание постов из нескольких документов

    Args:
        api_key: API ключ
        documents: список текстов документов
        template: шаблон для всех постов
        **kwargs: дополнительные параметры для create_post_from_document

    Returns:
        список результатов
    """
    results = []

    for i, doc in enumerate(documents):
        print(f"Обработка документа {i + 1}/{len(documents)}...")
        result = create_post_from_document(
            api_key=api_key,
            document_text=doc,
            template=template,
            **kwargs
        )
        results.append(result)

    return results


# Пример использования
def main():
    # Ваш API ключ
    API_KEY = "your-api-key-here"

    # Пример документа
    document = """
    Наша компания выпустила новую версию программного обеспечения для управления проектами. 
    Новая версия включает в себя: улучшенный интерфейс, интеграцию с популярными сервисами, 
    автоматическое планирование задач и аналитику в реальном времени. 
    Обновление доступно для всех пользователей с 1 марта 2024 года.
    """

    # Создаем пост для соцсетей
    result = create_post_from_document(
        api_key=API_KEY,
        document_text=document,
        template="social",
        tone="enthusiastic",
        max_length=300,
        language="ru"
    )

    if result["success"]:
        print("=== Созданный пост ===")
        print(result["post"])
        print(f"\nДлина: {result['length']} символов")
        print(f"Шаблон: {result['template_used']}")
    else:
        print(f"Ошибка: {result['error']}")

    # Пример с разными шаблонами
    templates_to_try = ["social", "blog", "news", "teaser"]

    for template in templates_to_try:
        print(f"\n\n--- Шаблон: {template} ---")
        result = create_post_from_document(
            api_key=API_KEY,
            document_text=document,
            template=template,
            max_length=400
        )

        if result["success"]:
            print(result["post"])


# Класс для более удобной работы
class DocumentToPostConverter:
    """Класс для конвертации документов в посты"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.templates = ["default", "social", "blog", "news", "teaser"]

    def convert(self, document: str, template: str = "social", **kwargs) -> Optional[str]:
        """
        Конвертация документа в пост

        Args:
            document: текст документа
            template: шаблон поста
            **kwargs: дополнительные параметры

        Returns:
            текст поста или None
        """
        result = create_post_from_document(
            api_key=self.api_key,
            document_text=document,
            template=template,
            **kwargs
        )

        return result["post"] if result["success"] else None

    def compare_templates(self, document: str, **kwargs) -> Dict[str, Optional[str]]:
        """
        Сравнение всех шаблонов для одного документа

        Args:
            document: текст документа
            **kwargs: параметры для create_post_from_document

        Returns:
            словарь с результатами для каждого шаблона
        """
        results = {}

        for template in self.templates:
            print(f"Генерация для шаблона '{template}'...")
            results[template] = self.convert(document, template, **kwargs)

        return results


if __name__ == "__main__":
    # Пример использования класса
    API_KEY = "your-api-key-here"
    converter = DocumentToPostConverter(API_KEY)

    document = "Ваш текст документа здесь..."

    # Сравниваем разные шаблоны
    comparisons = converter.compare_templates(document, max_length=300)

    for template, post in comparisons.items():
        if post:
            print(f"\n=== {template.upper()} ===\n{post}\n")
            print("-" * 50)

# Пример использования
def main():
    # Замените на ваш реальный API ключ
    API_KEY = "your-api-key-here"

    # Создаем экземпляр бота
    bot = DeepSeekBot(API_KEY)

    print("Бот DeepSeek запущен! Введите 'exit' для выхода, 'clear' для очистки истории.")
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