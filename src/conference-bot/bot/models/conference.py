from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Conference:
  """
    Модель данных конференции
  """
  title: str # назваание
  date: datetime # дата проведения
  deadline: datetime # срок подачи заявки на участие
  description: Optional[str] = None # краткое описание
  tags: List[str] = field(default_factory=list) # теги
  file_id: Optional[str] = None # идентификатор в базе данных
  
  def to_post_text(self) -> str:
    """Форматирование в текст поста"""
    tags_str = " ".join(self.tags) if self.tags else ""
    return (
      f"<b>{self.title}</b>\n\n"
      f"📅 Дата: {self.date.strftime('%d.%m.%Y')}\n"
      f"⏰ Дедлайн: {self.deadline.strftime('%d.%m.%Y')}\n\n"
      f"{self.description or ''}\n\n"
      f"{tags_str}"
    ).strip()