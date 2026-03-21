# Database Module

Модуль для работы с базой данных конференций. Использует SQLite — файловая БД, не требует отдельного сервера.

## Структура

database/
├── __init__.py          # делает папку модулем Python
├── schema.py            # создание таблиц
├── db_manager.py        # функции для работы с данными
└── README.md            # эта документация

## Инициализация

Перед первым использованием нужно создать таблицы:

from database.schema import init_db

init_db()  # создаст файл conferences.db в корне проекта

## Функции (db_manager.py)

Все функции находятся в database.db_manager.

### add_conference(name, conference_date, location, submission_deadline)

Добавляет новую конференцию в базу данных.

Параметры:
- name (str) — название конференции
- conference_date (str) — дата проведения в формате YYYY-MM-DD
- location (str) — место проведения (город, страна)
- submission_deadline (str) — крайняя дата подачи заявки в формате YYYY-MM-DD

Возвращает: int — ID добавленной конференции

Пример:

from database.db_manager import add_conference

new_id = add_conference(
    name="AI Conference 2025",
    conference_date="2025-06-15",
    location="Moscow",
    submission_deadline="2025-04-01"
)
print(f"Добавлена конференция с ID {new_id}")

---

### search_conferences(query)

Ищет конференции по названию (частичное совпадение). Возвращает только активные (неархивированные).

Параметры:
- query (str) — текст для поиска

Возвращает: list of tuples — список конференций, каждая в формате:
(id, name, conference_date, location, submission_deadline, is_archived)

Пример:

from database.db_manager import search_conferences

results = search_conferences("AI")
for conf in results:
    print(f"{conf[1]} — {conf[2]} ({conf[3]})")

---

### get_active_conferences()

Возвращает все активные (неархивированные) конференции, отсортированные по дате проведения (от ближайшей к дальней).

Возвращает: list of tuples — список конференций (тот же формат, что и выше)

Пример:

from database.db_manager import get_active_conferences

active = get_active_conferences()
for conf in active:
    print(f"{conf[1]} | {conf[2]} | {conf[3]}")

---

### archive_past_conferences()

Архивирует все конференции, у которых дата проведения меньше текущей даты. Заархивированные конференции не отображаются в search_conferences() и get_active_conferences().

Возвращает: int — количество заархивированных конференций

Пример:

from database.db_manager import archive_past_conferences

count = archive_past_conferences()
print(f"Заархивировано конференций: {count}")

## Схема таблицы

Таблица conferences:

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER | Первичный ключ, автоинкремент |
| name | TEXT | Название конференции |
| conference_date | TEXT | Дата проведения (YYYY-MM-DD) |
| location | TEXT | Место проведения |
| submission_deadline | TEXT | Крайняя дата подачи заявки |
| is_archived | INTEGER | 0 — активна, 1 — заархивирована |

## Пример полного использования

from database.schema import init_db
from database.db_manager import (
    add_conference,
    search_conferences,
    get_active_conferences,
    archive_past_conferences
)

# 1. Создаём БД
init_db()

# 2. Добавляем конференции
add_conference("AI Conference 2025", "2025-06-15", "Moscow", "2025-04-01")
add_conference("ML Summit 2025", "2025-05-10", "Saint Petersburg", "2025-03-01")

# 3. Ищем по названию
results = search_conferences("AI")
print(f"Найдено: {len(results)}")

# 4. Получаем все активные
active = get_active_conferences()
print(f"Всего активных: {len(active)}")

# 5. Архивируем прошедшие
archived = archive_past_conferences()
print(f"Заархивировано: {archived}")

## Примечания для команды

1. Файл БД (conferences.db) создаётся автоматически при вызове init_db()
2. Не коммитьте conferences.db в репозиторий — он должен быть в .gitignore
3. Все даты передаются в формате YYYY-MM-DD (например, 2025-06-15)
4. Функции возвращают данные в виде кортежей (tuple). Индексы:
   - 0 — id
   - 1 — name
   - 2 — conference_date
   - 3 — location
   - 4 — submission_deadline
   - 5 — is_archived