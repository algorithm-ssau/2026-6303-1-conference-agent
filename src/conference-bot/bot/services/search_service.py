from typing import List, Dict, Any
from dataclasses import dataclass
from bot.models.conference import Conference
from bot.core.constants import MESSAGES

@dataclass
class SearchResult:
  """
    Результат поиска
  """
  conference: Conference
  relevance: float
    
class SearchService:
  """
    Сервис для поиска конференций
  """
  
  def __init__(self):
    # В будущем здесь будет подключение к БД или API
    self.conferences: List[Conference] = []
  
  async def search(self, query: str, limit: int = 5, offset: int = 0) -> Dict[str, Any]:
    """
      Выполняет поиск конференций по запросу
      Возвращает результаты и информацию для пагинации
    """
    # заглушка - в будущем реальный поиск
    mock_results = []
    # /заглушка
    
    # переделать
    if query.lower() == "test":
      for i in range(10):
        mock_results.append(
          SearchResult(
            conference=Conference(
              title=f"Конференция {i+1} по теме '{query}'",
              date=None,
              deadline=None
            ),
            relevance=1.0
          )
        )
    else:
      # Обычный поиск - 3 результата
      for i in range(3):
        mock_results.append(
          SearchResult(
            conference=Conference(
              title=f"Конференция {i+1} по теме '{query}'",
              date=None,
              deadline=None
            ),
            relevance=1.0
          )
        )
    
    total = len(mock_results)
    has_more = offset + limit < total
    results = mock_results[offset:offset + limit]
    
    return {
      "results": results,
      "total": total,
      "has_more": has_more,
      "offset": offset,
      "limit": limit
    }
  
  @staticmethod
  def format_search_results(results: List[SearchResult]) -> str:
    """
      Форматирует результаты поиска для отображения
    """
    if not results:
      return MESSAGES["errors"]["confs-not-found"]
  
    return MESSAGES["search-conf"]["conf-list-stub"]
  
  
  @staticmethod
  def parse_offset(callback_data: str) -> int:
    try:
      return int(callback_data.split(":")[1])
    except:
      return 0