import logging
from typing import Dict, Any, Optional
from bot.models.conference import Conference
from bot.core.constants import MESSAGES
from bot.database.db_manager import add_conference
from bot.database import conference_repository
from bot.services.parser.models import EventData
from bot.config import TAG_RULES
from bot.services.post_service import PostService
from html import escape
from bot.services.parser.parser_service import ParserService


post_service = PostService()

class ConferenceService:
  """
    Сервис для управления процессом создания конференции
  """
  

  @staticmethod
  async def parse_file(file_path: str) -> dict | None:
    """
    Обрабатывает PDF:
    1. Извлекает текст (OCR при необходимости)
    2. Прогоняет через LLM
    3. Возвращает структурированные данные
    """
    parser_service = ParserService()
    
    parsed = await parser_service.parse_pdf(file_path)

    if not parsed:
      logging.error("❌ LLM не вернул данные для парсинга")
      return None

    try:
      validated = EventData(**parsed)
      return validated.model_dump()
    except Exception as e:
      logging.exception(f"Ошибка валидации Pydantic: {e}")
      logging.error(f"Полученные данные: {parsed}")  # ← Важно!
      return None
    
  @staticmethod
  async def get_smart_tags(text: str) -> list[str]:
      text_lower = text.lower()
      reserved_tags = []
      
      # 1. Поиск по зарезервированному словарю (максимум 3)
      for tag, keywords in TAG_RULES.items():
          if any(kw.lower() in text_lower for kw in keywords):
              reserved_tags.append(tag)
              if len(reserved_tags) == 3:
                  break
      
      # Получаем все теги из словаря для исключения
      all_reserved_tags = list(TAG_RULES.keys())
                  
      # 2. Генерация через LLM с передачей списка исключений
      llm_tags = await post_service.generate_tags(text, max_tags=7, exclude_tags=all_reserved_tags)
        
      # 3. Объединение с дополнительной программной проверкой
      final_tags = reserved_tags.copy()
      for tag in llm_tags:
          tag_lower = tag.lower()
          # Добавляем, только если тега еще нет в final_tags И он не совпадает ни с одним из TAG_RULES
          if tag not in final_tags and tag_lower not in all_reserved_tags:
              final_tags.append(tag)
              
      return final_tags

  @staticmethod
  def toggle_tag(draft: Dict[str, Any], tag: str) -> Dict[str, Any]:
    """
      Переключает тег в черновике
    """
    selected = draft.get("selected_tags", []).copy()
    
    if tag in selected:
      selected.remove(tag)
    else:
      selected.append(tag)
    
    return {
      **draft,
      "selected_tags": selected
    }
  
  
  @staticmethod
  def add_tag(draft: Dict[str, Any], new_tag: str) -> Dict[str, Any]:
    """
      Добавляет новый тег в черновик
    """
    if not new_tag.startswith("#"):
      new_tag = "#" + new_tag
    
    available = draft.get("available_tags", []).copy()
    selected = draft.get("selected_tags", []).copy()
    
    if new_tag not in available:
      available.append(new_tag)
    
    if new_tag not in selected:
      selected.append(new_tag)
    
    return {
      **draft,
      "available_tags": available,
      "selected_tags": selected
    }
  
  
  @staticmethod
  async def build_post(draft: Dict[str, Any]) -> str:
    """
      Строит текст поста из черновика
    """
    selected_tags = draft.get("selected_tags", [])
    
    parsed = draft.get("parsed_data", {})

    source_text = f"""
    Название: {parsed.get('event_name')}
    Даты: {parsed.get('dates')}
    Место: {parsed.get('location')}
    Описание: {parsed.get('topics')}
    """
    post_text = await post_service.generate_post(source_text)
    
    if not post_text:
      return "❌ Не удалось сгенерировать пост"

    # TODO: сделать обработку ошибки здесь

    formatted_post = (
      MESSAGES["publish-post"]["post-preview"]
      + "<blockquote>" + escape(post_text) + "</blockquote>"
    )
    
    if selected_tags:
      formatted_post += "\n\n" + " ".join(selected_tags)
    
    return formatted_post
  
  
  @staticmethod
  async def publish_post(conference: Conference, channel_id: Optional[str] = None) -> bool:
    """
      Публикует пост о конференции
      В будущем здесь будет реальная публикация
    """
    # заглушка
    print(f"Публикация конференции: {conference.title}")
    # /заглушка
    
    return True
  
  """Добавление конференции в БД"""
  
  @staticmethod
  async def create_conference(data: dict):
    return await conference_repository.ConferenceRepository.create(data)
  

  @staticmethod
  def format_parsed_data(data: dict) -> str:
    return (
      f"📌 Название: {data.get('event_name')}\n"
      f"📅 Даты: {data.get('dates')}\n"
      f"📍 Место: {data.get('location')}\n"
    )
      

  @staticmethod
  def save_to_db(data: dict):
    conference_dict = {
      "name": data.get("event_name"),
      "conference_date": data.get("dates"),
      "location": data.get("location"),
      "submission_deadline": None,
      "event_type": data.get("event_type"),
      "organizer": data.get("organizer"),
      "dates": data.get("dates"),
      "status": data.get("status", "active"),
      "rsci": data.get("rsci", False),
      "format": data.get("format"),
      "target_audience": data.get("target_audience")
    }
    return add_conference(conference_dict)
  
  
  @staticmethod
  async def parse_text(text: str):
    parser_service = ParserService()
    return await parser_service.parser.parse(text)