import asyncio
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from bot.models.conference import Conference
from bot.database.db_manager import get_active_conferences
from bot.core.constants import MESSAGES

MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
SIMILARITY_THRESHOLD = 0.35  # Порог снижен для более лояльного поиска по предложениям

@dataclass
class SearchResult:
  conference: Conference
  relevance: float

class SearchService:
  _model = None
  _conference_cache = {}  # Кэш для эмбеддингов конференций: id -> vector
  @classmethod
  def _get_model(cls):
    # Синглтон-загрузка модели, чтобы не грузить ее при каждом запуске
    if cls._model is None:
      print("⏳ Загрузка модели SentenceTransformers (это может занять время)...")
      cls._model = SentenceTransformer(MODEL_NAME)
    return cls._model
  

  @staticmethod
  def _safe_parse_date(date_str: str) -> datetime:
    # Вспомогательная функция для парсинга строковых дат из БД в объект datetime
    if not date_str:
      return datetime.now()
    try:
      # Попытка распарсить стандартный YYYY-MM-DD
      return datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
    except Exception:
      return datetime.now()
      

  @staticmethod
  def _perform_cpu_search(query: str, active_confs: list) -> List[SearchResult]:
    """
      Синхронная функция для выполнения математических расчетов.
      Запускается в отдельном потоке.
    """
    model = SearchService._get_model()
    user_emb = model.encode([query])    # Преобразуем запрос пользователя в вектор
    
    results = []
    for row in active_confs:
      conf_id = row.get('id')
      name = row.get('name') or ""
      event_type = row.get('event_type') or ""
      organizer = row.get('organizer') or ""
      dates_str = row.get('conference_date') or ""
      deadline_str = row.get('submission_deadline') or ""
      audience = row.get('target_audience') or ""
      tags_str = row.get('tags') or ""
      # Формируем текст для сравнения из того, что есть в БД (вместо topics)
      text_to_encode = f"{name}. {event_type}. Аудитория: {audience}. Теги: {tags_str}"
      # Считаем эмбеддинг конференции только 1 раз и кэшируем
      if conf_id not in SearchService._conference_cache:
        SearchService._conference_cache[conf_id] = model.encode([text_to_encode])
      
      conf_emb = SearchService._conference_cache[conf_id]
      
      # Считаем косинусное сходство
      score = float(cosine_similarity(user_emb, conf_emb)[0][0])
      if score >= SIMILARITY_THRESHOLD:
        conf_obj = Conference(
          title=name,
          date=SearchService._safe_parse_date(dates_str),
          deadline=SearchService._safe_parse_date(deadline_str),
          description=f"{event_type}\nОрганизатор: {organizer}",
          tags=[]
        )
        results.append(SearchResult(conference=conf_obj, relevance=score))
    # Сортируем по убыванию релевантности
    results.sort(key=lambda x: x.relevance, reverse=True)
    return results
  

  async def search(self, query: str, limit: int = 5, offset: int = 0) -> Dict[str, Any]:
    # Быстрый синхронный запрос к SQLite
    active_confs = get_active_conferences()
    
    if not active_confs:
      return {"results": [], "total": 0, "has_more": False, "offset": offset, "limit": limit}
    # Передаем тяжелые вычисления в фоновый поток (чтобы бот не зависал)
    all_results = await asyncio.to_thread(
      self._perform_cpu_search, 
      query, 
      active_confs
    )
    total = len(all_results)
    has_more = offset + limit < total
    paged_results = all_results[offset:offset + limit]
    
    return {
      "results": paged_results,
      "total": total,
      "has_more": has_more,
      "offset": offset,
      "limit": limit
    }


  @staticmethod
  def format_search_results(results: List[SearchResult]) -> str:
    if not results:
      return "К сожалению, по данному запросу подходящих конференций не найдено."
    
    formatted = "<b>🔍 Найдено по вашему запросу:</b>\n\n"
    for i, res in enumerate(results, 1):
      formatted += f"{i}. {res.conference.to_post_text()}\n<i>Совпадение: {int(res.relevance * 100)}%</i>\n----------\n"
    
    return formatted