# database/db_manager.py
import sqlite3

DB_PATH = 'conferences.db'

def add_conference(name, conference_date, location, submission_deadline):
  """
    Добавляет новую конференцию в базу данных.

    :param name: Название конференции
    :param conference_date: Дата проведения (YYYY-MM-DD)
    :param location: Место проведения
    :param submission_deadline: Дедлайн подачи заявок (YYYY-MM-DD)
    :return: ID добавленной записи
  """
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
    INSERT INTO conferences (name, conference_date, location, submission_deadline)
    VALUES (?, ?, ?, ?)
  ''', (name, conference_date, location, submission_deadline))
  conn.commit()
  conn.close()
  return cursor.lastrowid

def search_conferences(query):
  """
    Выполняет поиск конференций по части названия.

    :param query: Строка поиска
    :return: Список кортежей с конференциями (только неархивированные)
  """
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
    SELECT * FROM conferences 
    WHERE name LIKE ? AND is_archived = 0
    ORDER BY conference_date
  ''', (f'%{query}%',))
  results = cursor.fetchall()
  conn.close()
  return results

def get_active_conferences():
  """
    Возвращает все актуальные (неархивированные) конференции.

    :return: Список конференций, отсортированных по дате
  """
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
    SELECT * FROM conferences 
    WHERE is_archived = 0
    ORDER BY conference_date
  ''')
  results = cursor.fetchall()
  conn.close()
  return results

def archive_past_conferences():
  """
    Помечает прошедшие конференции как архивные.

    :return: Количество обновленных записей
  """
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
    UPDATE conferences 
    SET is_archived = 1 
    WHERE conference_date < date('now')
  ''')
  conn.commit()
  conn.close()
  return cursor.rowcount  # сколько записей заархивировано