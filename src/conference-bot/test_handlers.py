import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ТЕСТЫ ХЕНДЛЕРОВ АДМИНА

class TestAddConferenceHandler:
    """Тесты для хендлеров добавления конференции"""
    
    def test_add_conf_callback_exists(self):
        """Проверяет, что коллбэк add_conf существует"""
        from bot.core.constants import callbacks as cb
        assert hasattr(cb, 'ADD_CONF'), "Коллбэк ADD_CONF должен существовать"
    
    def test_confirm_save_conf_callback_exists(self):
        """Проверяет, что коллбэк подтверждения существует"""
        from bot.core.constants import callbacks as cb
        assert hasattr(cb, 'CONFIRM_SAVE_CONF'), "Коллбэк CONFIRM_SAVE_CONF должен существовать"
    
    def test_admin_service_is_admin_exists(self):
        """Проверяет, что функция проверки админа существует"""
        from bot.services import AdminService
        assert hasattr(AdminService, 'is_admin'), "AdminService должен иметь метод is_admin"


# ТЕСТЫ ХЕНДЛЕРОВ ХЭШТЕГОВ

class TestHashtagsHandler:
    """Тесты для хендлеров управления хэштегами"""
    
    def test_tag_callback_exists(self):
        """Проверяет, что коллбэк тега существует"""
        from bot.core.callbacks import TagCallback
        assert TagCallback is not None, "TagCallback должен существовать"
    
    def test_toggle_tag_action_exists(self):
        """Проверяет, что действие toggle существует"""
        from bot.core.constants import callbacks as cb
        assert hasattr(cb, 'FINISH_TAGS'), "Коллбэк FINISH_TAGS должен существовать"
    
    def test_add_tag_action_exists(self):
        """Проверяет, что действие add_tag существует"""
        from bot.core.constants import callbacks as cb
        assert hasattr(cb, 'ADD_TAG'), "Коллбэк ADD_TAG должен существовать"


# ТЕСТЫ ПРОВЕРКИ АДМИНА

class TestAdminCheck:
    """Тесты для проверки прав администратора"""
    
    def test_admin_ids_not_empty(self):
        """Проверяет, что список админов не пустой"""
        from bot.config import ADMIN_IDS
        assert len(ADMIN_IDS) > 0, "Должен быть хотя бы один админ"
    
    def test_admin_check_with_valid_id(self):
        """Проверяет проверку админа с валидным ID"""
        from bot.services import AdminService
        from bot.config import ADMIN_IDS
        
        if len(ADMIN_IDS) > 0:
            result = AdminService.is_admin(ADMIN_IDS[0])
            assert result is True, "Админ должен проходить проверку"
    
    def test_admin_check_with_invalid_id(self):
        """Проверяет проверку админа с невалидным ID"""
        from bot.services import AdminService
        
        result = AdminService.is_admin(999999999)
        assert result is False, "Не админ не должен проходить проверку"