import sqlite3

DB_PATH = 'conferences.db'


class AdminRepository:

  @staticmethod
  def add_admin(username: str, added_by: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
      cursor.execute('''
        INSERT INTO admins (username, added_by)
        VALUES (?, ?)
      ''', (username, added_by))

      conn.commit()
      return True

    except sqlite3.IntegrityError:
      return False  # уже существует

    finally:
      conn.close()


  @staticmethod
  def is_admin(username: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
      'SELECT 1 FROM admins WHERE username = ?',
      (username,)
    )

    result = cursor.fetchone()
    conn.close()
    return result is not None


  @staticmethod
  def get_all() -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT username FROM admins')
    rows = cursor.fetchall()

    conn.close()
    return [r[0] for r in rows]