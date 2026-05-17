import sqlite3

DB_PATH = 'conferences.db'

def init_db():

  """
    Инициализирует базу данных и создает таблицу conferences,
    если она еще не существует.
  """
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS conferences (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      event_type TEXT,
      organizer TEXT,
      dates TEXT,
      status TEXT,
      conference_date TEXT,
      location TEXT,
      submission_deadline TEXT,
      rsci INTEGER DEFAULT 0,
      format TEXT,
      target_audience TEXT,
      is_archived INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      tags TEXT,  -- Новое поле для тегов
      UNIQUE(name, conference_date)
    )
  ''')

   # Миграция: если таблица уже создана без tags, добавляем колонку
  try:
    cursor.execute("ALTER TABLE conferences ADD COLUMN tags TEXT;")
  except sqlite3.OperationalError:
    pass  # Колонка уже существует
      
  conn.commit()
  conn.close()

