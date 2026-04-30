import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ТЕСТЫ PYDANTIC МОДЕЛИ EVENTDATA

class TestEventDataModel:
    """Тесты для проверки модели данных конференции"""
    
    def test_valid_event_data_passes(self):
        """Проверяет, что валидные данные проходят валидацию"""
        from bot.services.parser.models import EventData
        data = EventData(
            event_name="AI Conference 2024",
            dates="2024-12-01 - 2024-12-03",
            location="Moscow",
            rsci=True
        )
        assert data.event_name == "AI Conference 2024"
        assert data.rsci is True
    
    def test_event_data_with_optional_fields(self):
        """Проверяет, что модель работает с опциональными полями"""
        from bot.services.parser.models import EventData
        data = EventData()
        assert data.event_name is None
        assert data.location is None
    
    def test_event_data_with_deadlines(self):
        """Проверяет, что дедлайны корректно создаются"""
        from bot.services.parser.models import EventData, DeadlineInfo
        data = EventData(
            event_name="Test Conference",
            deadlines=[
                DeadlineInfo(date="2024-11-01", description="Регистрация"),
                DeadlineInfo(date="2024-11-15", description="Подача тезисов")
            ]
        )
        assert len(data.deadlines) == 2
        assert data.deadlines[0].date == "2024-11-01"
    
    def test_event_data_with_links(self):
        """Проверяет, что ссылки корректно создаются"""
        from bot.services.parser.models import EventData, LinkInfo
        data = EventData(
            event_name="Test Conference",
            links=[
                LinkInfo(url="https://example.com", description="Регистрация")
            ]
        )
        assert len(data.links) == 1
        assert "example.com" in data.links[0].url
    
    def test_event_data_with_topics_list(self):
        """Проверяет, что список тем корректно создаётся"""
        from bot.services.parser.models import EventData
        data = EventData(
            event_name="Test Conference",
            topics=["AI", "Machine Learning", "Data Science"]
        )
        assert len(data.topics) == 3
        assert "AI" in data.topics
    
    def test_event_data_model_dump(self):
        """Проверяет, что model_dump возвращает словарь"""
        from bot.services.parser.models import EventData
        data = EventData(
            event_name="Test Conference",
            dates="2024-12-01",
            location="Moscow"
        )
        dumped = data.model_dump()
        assert isinstance(dumped, dict)
        assert dumped["event_name"] == "Test Conference"


# ТЕСТЫ DEADLINEINFO МОДЕЛИ

class TestDeadlineInfoModel:
    """Тесты для модели дедлайнов"""
    
    def test_deadline_info_creation(self):
        """Проверяет создание информации о дедлайне"""
        from bot.services.parser.models import DeadlineInfo
        deadline = DeadlineInfo(date="2024-11-01", description="Регистрация")
        assert deadline.date == "2024-11-01"
        assert deadline.description == "Регистрация"
    
    def test_deadline_info_required_fields(self):
        """Проверяет, что обязательные поля должны быть заполнены"""
        from bot.services.parser.models import DeadlineInfo
        with pytest.raises(Exception):
            DeadlineInfo()


# ТЕСТЫ LINKINFO МОДЕЛИ

class TestLinkInfoModel:
    """Тесты для модели ссылок"""
    
    def test_link_info_creation(self):
        """Проверяет создание информации о ссылке"""
        from bot.services.parser.models import LinkInfo
        link = LinkInfo(url="https://example.com", description="Сайт конференции")
        assert link.url == "https://example.com"
        assert "сайт" in link.description.lower()
    
    def test_link_info_required_fields(self):
        """Проверяет, что обязательные поля должны быть заполнены"""
        from bot.services.parser.models import LinkInfo
        with pytest.raises(Exception):
            LinkInfo()