import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ТЕСТЫ CONFERENCE SERVICE (БИЗНЕС-ЛОГИКА)

class TestConferenceService:
    """Тесты для сервиса управления конференциями"""
    
    def test_get_default_tags_returns_list(self):
        """Проверяет, что дефолтные теги возвращаются списком"""
        from bot.services import ConferenceService
        tags = ConferenceService.get_default_tags()
        assert isinstance(tags, list), "Теги должны быть списком"
        assert len(tags) > 0, "Список тегов не должен быть пустым"
    
    def test_toggle_tag_adds_new_tag(self):
        """Проверяет, что toggle_tag добавляет новый тег"""
        from bot.services import ConferenceService
        draft = {"selected_tags": []}
        result = ConferenceService.toggle_tag(draft, "#ai")
        assert "#ai" in result["selected_tags"], "Тег должен добавиться"
    
    def test_toggle_tag_removes_existing_tag(self):
        """Проверяет, что toggle_tag удаляет существующий тег"""
        from bot.services import ConferenceService
        draft = {"selected_tags": ["#ai", "#ml"]}
        result = ConferenceService.toggle_tag(draft, "#ai")
        assert "#ai" not in result["selected_tags"], "Тег должен удалиться"
        assert "#ml" in result["selected_tags"], "Другие теги должны остаться"
    
    def test_add_tag_adds_hash_prefix(self):
        """Проверяет, что add_tag добавляет # если его нет"""
        from bot.services import ConferenceService
        draft = {"available_tags": [], "selected_tags": []}
        result = ConferenceService.add_tag(draft, "science")
        assert "#science" in result["available_tags"], "Должен добавиться # префикс"
    
    def test_add_tag_does_not_duplicate(self):
        """Проверяет, что add_tag не дублирует теги"""
        from bot.services import ConferenceService
        draft = {"available_tags": ["#ai"], "selected_tags": ["#ai"]}
        result = ConferenceService.add_tag(draft, "#ai")
        assert result["available_tags"].count("#ai") == 1, "Не должно быть дубликатов"
    
    def test_build_post_includes_selected_tags(self):
        """Проверяет, что build_post включает выбранные теги в пост"""
        from bot.services import ConferenceService
        draft = {"selected_tags": ["#ai", "#ml"]}
        with patch("bot.services.post_service.PostService.generate_post", return_value="Тест пост"):
            post = ConferenceService.build_post(draft)
            assert "#ai" in post, "Пост должен содержать выбранные теги"
            assert "#ml" in post, "Пост должен содержать все выбранные теги"
    
    def test_format_parsed_data_returns_formatted_string(self):
        """Проверяет форматирование данных конференции"""
        from bot.services import ConferenceService
        data = {
            "event_name": "AI Conference",
            "dates": "2024-12-01",
            "location": "Moscow"
        }
        result = ConferenceService.format_parsed_data(data)
        assert "AI Conference" in result, "Название должно быть в выводе"
        assert "2024-12-01" in result, "Дата должна быть в выводе"
        assert "Moscow" in result, "Место должно быть в выводе"