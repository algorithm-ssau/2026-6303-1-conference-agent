import pytest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.core.constants.callbacks import (
    ADD_CONF, OCR_OK, OCR_EDIT, DATA_OK, DATA_REGEN,
    FINISH_TAGS, ADD_TAG, PUBLISH, SAVE, ADD_ADMIN,
    MAIN_MENU, ABOUT, SEARCH, MORE, TOGGLE_TAG
)
from bot.core.constants.messages import MESSAGES

# =============================================================================
# ТЕСТЫ КОЛЛБЭКОВ (CALLBACKS.PY)
# =============================================================================

class TestAdminCallbacks:
    """Тесты для коллбэков администратора"""
    
    def test_add_conf_callback_exists(self):
        """Проверяет, что коллбэк добавления конференции существует"""
        assert ADD_CONF is not None, "ADD_CONF не должен быть None"
        assert len(ADD_CONF.strip()) > 0, "ADD_CONF не должен быть пустой строкой"
    
    def test_publish_callback_exists(self):
        """Проверяет, что коллбэк публикации существует"""
        assert PUBLISH is not None, "PUBLISH не должен быть None"
        assert len(PUBLISH.strip()) > 0, "PUBLISH не должен быть пустой строкой"
    
    def test_save_callback_exists(self):
        """Проверяет, что коллбэк сохранения существует"""
        assert SAVE is not None, "SAVE не должен быть None"
        assert len(SAVE.strip()) > 0, "SAVE не должен быть пустой строкой"
    
    def test_add_admin_callback_exists(self):
        """Проверяет, что коллбэк добавления админа существует (из TODO)"""
        assert ADD_ADMIN is not None, "ADD_ADMIN не должен быть None"
        assert len(ADD_ADMIN.strip()) > 0, "ADD_ADMIN не должен быть пустой строкой"

class TestUserCallbacks:
    """Тесты для коллбэков пользователя"""
    
    def test_main_menu_callback_exists(self):
        """Проверяет, что коллбэк главного меню существует"""
        assert MAIN_MENU is not None, "MAIN_MENU не должен быть None"
        assert len(MAIN_MENU.strip()) > 0, "MAIN_MENU не должен быть пустой строкой"
    
    def test_about_callback_exists(self):
        """Проверяет, что коллбэк 'О боте' существует"""
        assert ABOUT is not None, "ABOUT не должен быть None"
        assert len(ABOUT.strip()) > 0, "ABOUT не должен быть пустой строкой"
    
    def test_search_callback_exists(self):
        """Проверяет, что коллбэк поиска существует"""
        assert SEARCH is not None, "SEARCH не должен быть None"
        assert len(SEARCH.strip()) > 0, "SEARCH не должен быть пустой строкой"

class TestCallbacksUnique:
    """Проверяет уникальность коллбэков"""
    
    def test_no_duplicate_callbacks(self):
        """Проверяет, что все коллбэки уникальны (нет повторений)"""
        all_callbacks = [
            ADD_CONF, OCR_OK, OCR_EDIT, DATA_OK, DATA_REGEN,
            FINISH_TAGS, ADD_TAG, PUBLISH, SAVE, ADD_ADMIN,
            MAIN_MENU, ABOUT, SEARCH, MORE
        ]
        # Фильтруем None
        callbacks = [cb for cb in all_callbacks if cb is not None]
        assert len(callbacks) == len(set(callbacks)), "Обнаружены дубликаты в коллбэках!"

# =============================================================================
# ТЕСТЫ СООБЩЕНИЙ (MESSAGES.PY)
# =============================================================================

class TestMessages:
    """Тесты для сообщений бота"""
    
    def test_messages_dict_not_empty(self):
        """Проверяет, что словарь сообщений не пустой"""
        assert MESSAGES is not None, "MESSAGES не должен быть None"
        assert isinstance(MESSAGES, dict), "MESSAGES должен быть словарём"
        assert len(MESSAGES) > 0, "Словарь сообщений не должен быть пустым"
    
    def test_stub_post_exists(self):
        """Проверяет наличие шаблона поста для конференции"""
        assert "stub-post" in MESSAGES, "Отсутствует ключ 'stub-post'"
    
    def test_stub_post_has_text(self):
        """Проверяет, что у шаблона поста есть текст"""
        assert "text" in MESSAGES["stub-post"], "У stub-post должен быть ключ 'text'"
        assert isinstance(MESSAGES["stub-post"]["text"], str), "Текст должен быть строкой"
    
    def test_stub_post_length(self):
        """Проверяет, что текст поста достаточно длинный"""
        text = MESSAGES["stub-post"]["text"]
        assert len(text) > 100, "Текст поста слишком короткий (меньше 100 символов)"
    
    def test_stub_post_has_placeholders(self):
        """Проверяет наличие плейсхолдеров для замены данных"""
        text = MESSAGES["stub-post"]["text"]
        assert "[Название тематики]" in text, "Отсутствует плейсхолдер названия"
        assert "[Город/Университет/Площадка]" in text, "Отсутствует плейсхолдер места"
        assert "[Дата начала]" in text, "Отсутствует плейсхолдер даты"
    
    def test_about_message_exists(self):
        """Проверяет наличие сообщения 'О боте'"""
        assert "about" in MESSAGES, "Отсутствует ключ 'about'"
    
    def test_about_message_has_text(self):
        """Проверяет, что у 'О боте' есть текст"""
        assert "text" in MESSAGES["about"], "У about должен быть ключ 'text'"
        assert len(MESSAGES["about"]["text"]) > 0, "Текст 'О боте' не должен быть пустым"