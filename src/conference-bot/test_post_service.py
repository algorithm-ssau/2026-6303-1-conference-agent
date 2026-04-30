import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ТЕСТЫ POST SERVICE (ГЕНЕРАЦИЯ ПОСТОВ ЧЕРЕЗ AI)

class TestPostService:
    """Тесты для сервиса генерации постов"""
    
    def test_init_with_api_key(self):
        """Проверяет инициализацию сервиса с API ключом"""
        from bot.services.post_service import PostService
        service = PostService(api_key="test_key_123")
        assert service.api_key == "test_key_123"
        assert "Bearer test_key_123" in service.headers["Authorization"]
    
    def test_generate_post_default_template(self):
        """Проверяет генерацию поста с дефолтным шаблоном"""
        from bot.services.post_service import PostService
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Сгенерированный пост"}}]
            }
            mock_post.return_value = mock_response
            
            service = PostService(api_key="test_key")
            result = service.generate_post(text="Тестовый текст")
            
            assert result == "Сгенерированный пост"
            mock_post.assert_called_once()
    
    def test_generate_post_social_template(self):
        """Проверяет генерацию поста с социальным шаблоном"""
        from bot.services.post_service import PostService
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Пост для соцсетей с эмодзи 🎉"}}]
            }
            mock_post.return_value = mock_response
            
            service = PostService(api_key="test_key")
            result = service.generate_post(
                text="Тестовый текст",
                template="social"
            )
            
            assert "эмодзи" in result
            mock_post.assert_called_once()
    
    def test_generate_post_api_error(self):
        """Проверяет обработку ошибки API"""
        from bot.services.post_service import PostService
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response
            
            service = PostService(api_key="test_key")
            result = service.generate_post(text="Тестовый текст")
            
            assert result is None
    
    def test_generate_post_exception(self):
        """Проверяет обработку исключений"""
        from bot.services.post_service import PostService
        
        with patch("requests.post", side_effect=requests.exceptions.Timeout):
            service = PostService(api_key="test_key")
            result = service.generate_post(text="Тестовый текст")
            
            assert result is None
    
    def test_generate_post_truncates_long_text(self):
        """Проверяет, что длинный текст обрезается до 3000 символов"""
        from bot.services.post_service import PostService
        
        long_text = "A" * 5000
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Post"}}]
            }
            mock_post.return_value = mock_response
            
            service = PostService(api_key="test_key")
            service.generate_post(text=long_text)
            
            # Проверяем, что payload содержит текст не длиннее 3000 символов
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            prompt_text = payload["messages"][1]["content"]
            assert len(long_text[:3000]) <= 3000
    
    def test_headers_content_type(self):
        """Проверяет, что заголовки содержат Content-Type"""
        from bot.services.post_service import PostService
        service = PostService(api_key="test_key")
        assert service.headers["Content-Type"] == "application/json"
    
    def test_generate_post_with_custom_parameters(self):
        """Проверяет генерацию поста с кастомными параметрами"""
        from bot.services.post_service import PostService
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Custom post"}}]
            }
            mock_post.return_value = mock_response
            
            service = PostService(api_key="test_key")
            service.generate_post(
                text="Test",
                tone="casual",
                max_length=1000,
                language="en"
            )
            
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["max_tokens"] == 2000  # max_length * 2


# ТЕСТЫ ИНТЕГРАЦИИ POST SERVICE С CONFERENCE SERVICE

class TestPostServiceIntegration:
    """Интеграционные тесты PostService с ConferenceService"""
    
    def test_conference_service_uses_post_service(self):
        """Проверяет, что ConferenceService использует PostService"""
        from bot.services import ConferenceService
        
        draft = {"selected_tags": ["#ai"]}
        
        with patch("bot.services.post_service.PostService.generate_post", return_value="Generated post"):
            post = ConferenceService.build_post(draft)
            
            assert "Generated post" in post
            assert "#ai" in post