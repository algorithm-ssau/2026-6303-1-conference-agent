import pytest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from bot.config import TOKEN
from bot.core.constants.messages import MESSAGES

# Тест 1: Проверяем токен
def test_token_exists():
    assert len(TOKEN) > 10, "Токен слишком короткий!"

# Тест 2: Проверяем сообщения
def test_messages_loaded():
    assert len(MESSAGES) > 0, "Сообщения пустые!"
    assert "stub-post" in MESSAGES, "Нет шаблона поста!"