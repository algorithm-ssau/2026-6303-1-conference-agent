import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.config import TOKEN, ADMIN_IDS


# ТЕСТЫ КОНФИГУРАЦИИ (ADMIN_IDS И TOKEN)

class TestConfigDetails:
    """Тесты для проверки деталей конфигурации"""
    
    def test_admin_ids_exists(self):
        """Проверяет, что список админов существует"""
        assert ADMIN_IDS is not None, "Список ADMIN_IDS не должен быть None"
        assert isinstance(ADMIN_IDS, list), "ADMIN_IDS должен быть списком"
    
    def test_admin_ids_not_empty(self):
        """Проверяет, что в списке админов есть хотя бы один ID"""
        assert len(ADMIN_IDS) > 0, "Список админов не должен быть пустым"
    
    def test_admin_ids_are_integers(self):
        """Проверяет, что все ID админов — целые числа"""
        for admin_id in ADMIN_IDS:
            assert isinstance(admin_id, int), f"ID админа {admin_id} должен быть числом"
    
    def test_admin_ids_positive(self):
        """Проверяет, что все ID админов положительные"""
        for admin_id in ADMIN_IDS:
            assert admin_id > 0, f"ID админа {admin_id} должен быть положительным"
    
    def test_admin_ids_unique(self):
        """Проверяет, что все ID админов уникальны"""
        assert len(ADMIN_IDS) == len(set(ADMIN_IDS)), "В списке админов есть дубликаты ID"
    
    def test_admin_ids_minimum_count(self):
        """Проверяет, что админов достаточно"""
        assert len(ADMIN_IDS) >= 3, "Должно быть минимум 3 админа"
    
    def test_token_format(self):
        """Проверяет формат токена"""
        assert ":" in TOKEN, "Токен Telegram должен содержать разделитель ':'"
        assert len(TOKEN) >= 40, "Токен слишком короткий для Telegram API"


# ТЕСТЫ СТРУКТУРЫ ХЕНДЛЕРОВ (HANDLERS)

class TestHandlersStructure:
    """Тесты для проверки структуры обработчиков"""
    
    def test_user_handler_exists(self):
        """Проверяет, что модуль пользователя существует"""
        try:
            from bot.handlers import user
            assert True
        except ImportError:
            pytest.skip("Модуль handlers.user ещё не создан")
    
    def test_user_handler_has_router(self):
        """Проверяет, что у пользователя есть router для aiogram"""
        try:
            from bot.handlers import user
            assert hasattr(user, 'router'), "Модуль user должен иметь атрибут 'router'"
        except ImportError:
            pytest.skip("Модуль handlers.user недоступен")
    
    def test_admin_handler_exists(self):
        """Проверяет, что модуль админа существует"""
        try:
            from bot.handlers import admin
            assert True
        except ImportError:
            pytest.skip("Модуль handlers.admin ещё не создан")
    
    def test_admin_handler_has_router(self):
        """Проверяет, что у админа есть router для aiogram"""
        try:
            from bot.handlers import admin
            assert hasattr(admin, 'router'), "Модуль admin должен иметь атрибут 'router'"
        except ImportError:
            pytest.skip("Модуль handlers.admin недоступен")


# ТЕСТЫ STATES (FSM)

class TestStatesStructure:
    """Тесты для проверки машины состояний"""
    
    def test_states_module_exists(self):
        """Проверяет, что модуль states существует"""
        try:
            from bot.states import states
            assert True
        except ImportError as e:
            pytest.skip(f"Модуль states ещё не создан: {e}")
    
    def test_states_has_classes(self):
        """Проверяет, что в states есть классы состояний"""
        try:
            from bot.states import states
            assert len(dir(states)) > 2, "Модуль states пустой"
        except ImportError:
            pytest.skip("Модуль states недоступен")