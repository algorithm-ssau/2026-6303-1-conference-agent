import sqlite3

DB_PATH = 'conferences.db'


def add_conference(data: dict) -> int | None:
    """
    Добавить новую конференцию из словаря.
    Возвращает ID или None, если конференция уже существует.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверка на дубликат
    cursor.execute('''
        SELECT id FROM conferences 
        WHERE name = ? AND conference_date = ?
    ''', (data.get('name'), data.get('conference_date')))
    
    if cursor.fetchone():
        conn.close()
        return None

    cursor.execute('''
        INSERT INTO conferences (
            name, event_type, organizer, dates, status,
            conference_date, location, submission_deadline,
            rsci, format, target_audience
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('event_type'),
        data.get('organizer'),
        data.get('dates'),
        data.get('status'),
        data.get('conference_date'),
        data.get('location'),
        data.get('submission_deadline'),
        1 if data.get('rsci') else 0,
        data.get('format'),
        data.get('target_audience')
    ))
    
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


def search_conferences(query: str) -> list:
    """Поиск по названию среди активных с будущим дедлайном."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM conferences 
        WHERE name LIKE ? 
          AND is_archived = 0
          AND submission_deadline >= date('now')
        ORDER BY submission_deadline
    ''', (f'%{query}%',))
    results = cursor.fetchall()
    conn.close()
    return results


def get_active_conferences() -> list:
    """Активные конференции с будущим дедлайном."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM conferences 
        WHERE is_archived = 0
          AND submission_deadline >= date('now')
        ORDER BY submission_deadline
    ''')
    results = cursor.fetchall()
    conn.close()
    return results


def archive_past_conferences() -> int:
    """Архивировать конференции с истекшим дедлайном."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE conferences 
        SET is_archived = 1 
        WHERE submission_deadline < date('now')
    ''')
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count
