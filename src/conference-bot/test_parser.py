import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ТЕСТЫ МОДЕЛЕЙ ПАРСЕРА

class TestParserModels:
    """Тесты для моделей парсера"""
    
    def test_event_data_is_pydantic_model(self):
        """Проверяет, что EventData — это Pydantic модель"""
        from bot.services.parser.models import EventData
        from pydantic import BaseModel
        
        assert issubclass(EventData, BaseModel), "EventData должен быть Pydantic моделью"
    
    def test_deadline_info_is_pydantic_model(self):
        """Проверяет, что DeadlineInfo — это Pydantic модель"""
        from bot.services.parser.models import DeadlineInfo
        from pydantic import BaseModel
        
        assert issubclass(DeadlineInfo, BaseModel), "DeadlineInfo должен быть Pydantic моделью"
    
    def test_link_info_is_pydantic_model(self):
        """Проверяет, что LinkInfo — это Pydantic модель"""
        from bot.services.parser.models import LinkInfo
        from pydantic import BaseModel
        
        assert issubclass(LinkInfo, BaseModel), "LinkInfo должен быть Pydantic моделью"
    
    def test_event_data_has_required_fields(self):
        """Проверяет наличие обязательных полей в EventData"""
        from bot.services.parser.models import EventData
        
        fields = EventData.model_fields
        assert 'event_name' in fields, "Должно быть поле event_name"
        assert 'dates' in fields, "Должно быть поле dates"
        assert 'location' in fields, "Должно быть поле location"
    
    def test_deadline_info_has_required_fields(self):
        """Проверяет наличие обязательных полей в DeadlineInfo"""
        from bot.services.parser.models import DeadlineInfo
        
        fields = DeadlineInfo.model_fields
        assert 'date' in fields, "Должно быть поле date"
        assert 'description' in fields, "Должно быть поле description"
    
    def test_link_info_has_required_fields(self):
        """Проверяет наличие обязательных полей в LinkInfo"""
        from bot.services.parser.models import LinkInfo
        
        fields = LinkInfo.model_fields
        assert 'url' in fields, "Должно быть поле url"
        assert 'description' in fields, "Должно быть поле description"


# ТЕСТЫ LLM PROVIDERS (С МОКАМИ)

class TestLLMProviders:
    """Тесты для провайдеров LLM"""
    
    def test_openrouter_provider_init(self):
        """Проверяет инициализацию OpenRouterProvider"""
        from bot.services.parser.llm_service import OpenRouterProvider
        
        provider = OpenRouterProvider(api_key="test_key", model="test_model")
        assert provider.api_key == "test_key"
        assert provider.model == "test_model"
    
    def test_groq_provider_init(self):
        """Проверяет инициализацию GroqProvider"""
        from bot.services.parser.llm_service import GroqProvider
        
        provider = GroqProvider(api_key="test_key", model="test_model")
        assert provider.api_key == "test_key"
        assert provider.model == "test_model"
    
    def test_fallback_parser_init(self):
        """Проверяет инициализацию FallbackLLMParser"""
        from bot.services.parser.llm_service import FallbackLLMParser, OpenRouterProvider
        
        providers = [OpenRouterProvider("key", "model")]
        parser = FallbackLLMParser(providers)
        assert len(parser.providers) == 1


# ТЕСТЫ CONFERENCE SERVICE PARSER

class TestConferenceServiceParser:
    """Тесты для парсинга в ConferenceService"""
    
    def test_parse_file_method_exists(self):
        """Проверяет, что метод parse_file существует"""
        from bot.services import ConferenceService
        assert hasattr(ConferenceService, 'parse_file'), "Должен быть метод parse_file"
    
    def test_get_default_tags_method_exists(self):
        """Проверяет, что метод get_default_tags существует"""
        from bot.services import ConferenceService
        assert hasattr(ConferenceService, 'get_default_tags'), "Должен быть метод get_default_tags"
    
    def test_format_parsed_data_method_exists(self):
        """Проверяет, что метод format_parsed_data существует"""
        from bot.services import ConferenceService
        assert hasattr(ConferenceService, 'format_parsed_data'), "Должен быть метод format_parsed_data"