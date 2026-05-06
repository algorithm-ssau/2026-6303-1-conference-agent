from typing import Dict, Any, List, Optional
from bot.models.conference import Conference
from bot.core.constants import MESSAGES
from bot.database.db_manager import add_conference
from bot.database import conference_repository
from bot.services.parser.text_extractor import PDFTextExtractor
from bot.services.parser.llm_service import OpenRouterProvider, GroqProvider, FallbackLLMParser
from bot.services.parser.models import EventData
from bot.config import OPENROUTER_API_KEY, GROQ_API_KEY, OPENROUTER_MODEL, GROQ_MODEL, DEEPSEEK_API_KEY
from bot.services.post_service import PostService

post_service = PostService(api_key=DEEPSEEK_API_KEY)

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

    extractor = PDFTextExtractor()

    providers = [
      GroqProvider(GROQ_API_KEY, GROQ_MODEL),
      OpenRouterProvider(OPENROUTER_API_KEY, OPENROUTER_MODEL),
    ]

    parser = FallbackLLMParser(providers)

    # 1. Извлекаем текст
    raw_text = extractor.extract_text_smart(file_path)

    if not raw_text.strip():
      return None

    # 2. Парсим через LLM
    parsed = parser.parse(raw_text)

    if not parsed:
      return None

    # 3. Валидируем через pydantic
    try:
      validated = EventData(**parsed)
      return validated.model_dump()
    except Exception as e:
      print(f"Ошибка валидации: {e}")
      return None
    
  @staticmethod
  def get_default_tags() -> List[str]:
    return ["#ai", "#ml", "#science"]
  
  
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
  def build_post(draft: Dict[str, Any]) -> str:
    """
      Строит текст поста из черновика
    """
    selected_tags = draft.get("selected_tags", [])
    
    parsed = draft.get("parsed_data", {})
    text = f"""
Название: {parsed.get('event_name')}
Даты: {parsed.get('dates')}
Место: {parsed.get('location')}
"""

    post_text = post_service.generate_post(" ") # подгружать здесь текст конференции

    if not post_text:
      return "❌ Не удалось сгенерировать пост"

    # сделать обработку ошибки здесь

    
    formatted_post = (
      MESSAGES["publish-post"]["post-preview"]
      + "<blockquote>" + post_text + "</blockquote>"
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
    return add_conference(
      name=data.get("event_name"),
      conference_date=data.get("dates"),
      location=data.get("location"),
      submission_deadline=None  # пока заглушка
    )