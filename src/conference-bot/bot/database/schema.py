# database/schema.py
import sqlite3

def init_db():
  """
    Инициализирует базу данных и создает таблицу conferences,
    если она еще не существует.
  """
  conn = sqlite3.connect('conferences.db')
  cursor = conn.cursor()
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS conferences (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      conference_date TEXT,
      location TEXT,
      submission_deadline TEXT,
      is_archived INTEGER DEFAULT 0
    )
  ''')
  conn.commit()
  conn.close()