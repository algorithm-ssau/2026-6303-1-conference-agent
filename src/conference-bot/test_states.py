import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ТЕСТЫ FSM СОСТОЯНИЙ

class TestAddConferenceStates:
    """Тесты для состояний добавления конференции"""
    
    def test_add_conference_class_exists(self):
        """Проверяет, что класс AddConference существует"""
        from bot.core.states.states import AddConference
        assert AddConference is not None, "Класс AddConference должен существовать"
    
    def test_waiting_for_file_state_exists(self):
        """Проверяет состояние ожидания файла"""
        from bot.core.states.states import AddConference
        assert hasattr(AddConference, 'waiting_for_file'), "Должно быть состояние waiting_for_file"
    
    def test_data_check_state_exists(self):
        """Проверяет состояние проверки данных"""
        from bot.core.states.states import AddConference
        assert hasattr(AddConference, 'data_check'), "Должно быть состояние data_check"
    
    def test_hashtags_state_exists(self):
        """Проверяет состояние хэштегов"""
        from bot.core.states.states import AddConference
        assert hasattr(AddConference, 'hashtags'), "Должно быть состояние hashtags"
    
    def test_post_state_exists(self):
        """Проверяет состояние поста"""
        from bot.core.states.states import AddConference
        assert hasattr(AddConference, 'post'), "Должно быть состояние post"
    
    def test_confirm_save_state_exists(self):
        """Проверяет состояние подтверждения сохранения"""
        from bot.core.states.states import AddConference
        assert hasattr(AddConference, 'confirm_save'), "Должно быть состояние confirm_save"
    
    def test_states_are_separate(self):
        """Проверяет, что состояния разные"""
        from bot.core.states.states import AddConference
        states = [
            AddConference.waiting_for_file,
            AddConference.data_check,
            AddConference.hashtags,
            AddConference.post,
            AddConference.confirm_save
        ]
        assert len(states) == len(set(states)), "Состояния должны быть уникальны"


# ТЕСТЫ СОСТОЯНИЙ ADDADMIN

class TestAddAdminStates:
    """Тесты для состояний добавления админа"""
    
    def test_add_admin_class_exists(self):
        """Проверяет, что класс AddAdmin существует"""
        from bot.core.states.states import AddAdmin
        assert AddAdmin is not None, "Класс AddAdmin должен существовать"
    
    def test_waiting_user_name_state_exists(self):
        """Проверяет состояние ожидания имени"""
        from bot.core.states.states import AddAdmin
        assert hasattr(AddAdmin, 'waiting_user_name'), "Должно быть состояние waiting_user_name"
    
    def test_add_new_admin_state_exists(self):
        """Проверяет состояние добавления админа"""
        from bot.core.states.states import AddAdmin
        assert hasattr(AddAdmin, 'add_new_admin'), "Должно быть состояние add_new_admin"


# ТЕСТЫ СОСТОЯНИЙ SEARCH

class TestSearchStates:
    """Тесты для состояний поиска"""
    
    def test_search_class_exists(self):
        """Проверяет, что класс Search существует"""
        from bot.core.states.states import Search
        assert Search is not None, "Класс Search должен существовать"
    
    def test_waiting_query_state_exists(self):
        """Проверяет состояние ожидания запроса"""
        from bot.core.states.states import Search
        assert hasattr(Search, 'waiting_query'), "Должно быть состояние waiting_query"


# ТЕСТЫ STATESGROUP

class TestStatesGroupStructure:
    """Тесты для проверки структуры StatesGroup"""
    
    def test_all_states_are_states_group(self):
        """Проверяет, что все классы наследуют StatesGroup"""
        from aiogram.fsm.state import StatesGroup
        from bot.core.states.states import AddConference, AddAdmin, Search
        
        assert issubclass(AddConference, StatesGroup), "AddConference должен наследовать StatesGroup"
        assert issubclass(AddAdmin, StatesGroup), "AddAdmin должен наследовать StatesGroup"
        assert issubclass(Search, StatesGroup), "Search должен наследовать StatesGroup"