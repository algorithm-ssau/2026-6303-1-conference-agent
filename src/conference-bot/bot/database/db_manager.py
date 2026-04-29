# database/db_manager.py
import sqlite3

DB_PATH = 'conferences.db'

def add_conference(name, conference_date, location, submission_deadline):
    """Добавить новую конференцию"""
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
    """Поиск по названию (или части названия)"""
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
    """Получить все активные конференции (сортировка по дате)"""
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
    """Архивировать конференции, которые уже прошли"""
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