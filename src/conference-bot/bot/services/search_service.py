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
    # user_emb = model.encode([query])
    user_emb = model.encode([query, *query.split(",")])
    user_emb = np.mean(user_emb, axis=0).reshape(1, -1)
    results = []
    
    for row in active_confs:
      emb_blob = row.get('embedding')
      if not emb_blob: continue # Пропускаем старые записи без векторов
      
      # Расшифровываем вектор: преобразуем байты обратно в матрицу
      conf_emb = np.frombuffer(emb_blob, dtype=np.float32).reshape(1, -1)
      score = float(cosine_similarity(user_emb, conf_emb)[0][0])
      
      if score >= SIMILARITY_THRESHOLD:
        conf_obj = Conference(
          title=row.get('name', ''),
          date=SearchService._safe_parse_date(row.get('conference_date', '')),
          deadline=SearchService._safe_parse_date(row.get('submission_deadline', '')),
          description=f"{row.get('event_type','')} {row.get('organizer','')}",
          tags=[]
        )
        results.append(SearchResult(conference=conf_obj, relevance=score))
            
    results.sort(key=lambda x: x.relevance, reverse=True)
    return results

  async def search(self, query: str, limit: int = 5, offset: int = 0) -> List[SearchResult]:
    # Быстрый синхронный запрос к SQLite
    active_confs = get_active_conferences()
    
    if not active_confs:
      return []
    # Передаем тяжелые вычисления в фоновый поток (чтобы бот не зависал)
    all_results = await asyncio.to_thread(self._perform_cpu_search, query, active_confs)
    return all_results[:limit]


  @staticmethod
  def format_search_results(results: List[SearchResult]) -> str:
    if not results:
      return "К сожалению, по данному запросу подходящих конференций не найдено."
    formatted = "🔍 Топ подходящих конференций:\n\n"
    for i, res in enumerate(results, 1):
      formatted += f"{i}. {res.conference.to_post_text()}\nСовпадение: {int(res.relevance * 100)}%\n———-\n"
    return formatted
  
  @classmethod
  def get_embedding_bytes(cls, text: str) -> bytes:
    model = cls._get_model()
    # Модель выдает массив numpy. Мы берем первый вектор и превращаем в байты
    return model.encode([text])[0].tobytes()