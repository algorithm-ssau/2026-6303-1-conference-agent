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
      topics TEXT,
      UNIQUE(name, conference_date)
    )
  ''')

   # Миграция: если таблица уже создана без tags, добавляем колонку
  try:
    cursor.execute("ALTER TABLE conferences ADD COLUMN tags TEXT;")
  except sqlite3.OperationalError:
    pass  # Колонка уже существует

  try:
    cursor.execute("ALTER TABLE conferences ADD COLUMN embedding BLOB;")
  except sqlite3.OperationalError:
    pass

  try:
    cursor.execute("ALTER TABLE conferences ADD COLUMN topics TEXT;")
  except sqlite3.OperationalError:
    pass


  cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      added_by INTEGER,
      created_at TEXT DEFAULT (datetime('now'))
    )
  ''')

      
  conn.commit()
  conn.close()

