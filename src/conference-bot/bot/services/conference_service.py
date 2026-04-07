from typing import Dict, Any, List, Optional
from bot.models.conference import Conference
from bot.repositories.conference_repository import ConferenceRepository
from bot.core.constants import MESSAGES

class ConferenceService:
  """
    Сервис для управления процессом создания конференции
  """

  
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
    
    # заглушка
    post_text = MESSAGES["stub-post"]["text"]
    # /заглушка
    
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
  
  '''
    Добавление конференции в БД
  '''
  
  @staticmethod
  async def create_conference(data: dict):
      return await ConferenceRepository.create(data)
  
 