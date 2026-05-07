import psycopg2
import requests
import json
import time
from datetime import datetime, timedelta, date

# ── Конфиг БД ───────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5430,
    "dbname":   "omstu_db",
    "user":     "omstu",
    "password": "omstu",
}

# ── API ─────────────────────────────────────────────
BASE_URL = "https://rasp.omgtu.ru/api/schedule"

# Период — 2 недели вперёд
DATE_FROM = date.today()
DATE_TO   = DATE_FROM + timedelta(weeks=2)

START = DATE_FROM.strftime("%Y.%m.%d")
FINISH = DATE_TO.strftime("%Y.%m.%d")

# ── Сущности ────────────────────────────────────────
GROUPS = [
    {"id": 483,  "name": "МО-221"},
    {"id": 484,  "name": "МО-231"},
    {"id": 485,  "name": "МО-241"},
    {"id": 486,  "name": "МО-251"},
    {"id": 685,  "name": "ФИТ-221"},
    {"id": 686,  "name": "ФИТ-222"},
    {"id": 687,  "name": "ФИТ-231"},
    {"id": 688,  "name": "ФИТ-232"},
    {"id": 689,  "name": "ФИТ-241"},
    {"id": 690,  "name": "ФИТ-242"},
]

TEACHERS = [
    {"id": 1004080,         "name": "ДЕВЯТЕРИКОВА М.В."},
    {"id": 1003031,         "name": "БОЛДОВСКАЯ Т.Е."},
    {"id": 1003027,         "name": "ЗАОЗЕРСКАЯ Л.А."},
    {"id": 1003026,         "name": "ГУНЕНКОВ М.Ю."},
    {"id": 665,             "name": "КОБЕРНИК Е.Г."},
    {"id": 1001178,         "name": "МАЛИЦКИЙ А.С."},
    {"id": 1001132,         "name": "ПОЛЯКОВА Т.А."},
    {"id": 999,             "name": "БЕЛИМ С.Ю."},
]

AUDITORIES = [
    {"id": 38,  "name": "Г-331"},
    {"id": 37,  "name": "Г-332"},
    {"id": 799, "name": "8-115"},
    {"id": 178, "name": "8-116"},
    {"id": 170, "name": "8-215"},
    {"id": 169, "name": "8-216"},
]

# ── Поля которые нужны Flutter клиенту ──────────────
REQUIRED_FIELDS = [
    "discipline",
    "kindOfWorkOid",
    "lecturer_title",
    "auditorium",
    "building",
    "beginLesson",
    "endLesson",
    "dayOfWeek",
    "date",
    "group",
    "subGroup",
    "stream",
    "lessonNumberStart",
]


def filter_lesson(lesson: dict) -> dict:
    """Оставляем только нужные Flutter полям поля."""
    return {field: lesson.get(field) for field in REQUIRED_FIELDS}


def fetch_schedule(entity_type: str, entity_id: int) -> list[dict]:
    """Запрашиваем расписание с API ОмГТУ."""
    url = f"{BASE_URL}/{entity_type}/{entity_id}"
    params = {"start": START, "finish": FINISH, "lng": 1}

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"  Ошибка запроса {url}: {e}")
        return []


def group_by_date(lessons: list[dict]) -> dict[str, list[dict]]:
    """Разбиваем список пар по датам."""
    by_date: dict[str, list] = {}
    for lesson in lessons:
        raw_date = lesson.get("date")
        if not raw_date:
            continue
        # Дата приходит в формате "2026.03.04" → нормализуем в "2026-03-04"
        try:
            parsed = datetime.strptime(raw_date, "%Y.%m.%d").date()
            key = parsed.isoformat()
        except ValueError:
            continue

        if key not in by_date:
            by_date[key] = []
        by_date[key].append(filter_lesson(lesson))

    return by_date


def upsert_cache(cur, entity_id: str, entity_type: str, schedule_date: str, data: list):
    """Вставляем или обновляем запись в schedule_cache."""
    cur.execute(
        """
        INSERT INTO schedule_cache (entity_id, entity_type, date, data, fetched_at)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (entity_id, entity_type, date)
        DO UPDATE SET
            data = EXCLUDED.data,
            fetched_at = NOW();
        """,
        (str(entity_id), entity_type, schedule_date, json.dumps(data, ensure_ascii=False))
    )


def seed():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    total_inserted = 0

    # ── Группы ──────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"Период: {START} → {FINISH}")
    print(f"{'='*50}\n")

    print("📚 Загружаем расписание групп...")
    for group in GROUPS:
        print(f"  Группа {group['name']} (id={group['id']})...")
        lessons = fetch_schedule("group", group["id"])
        by_date = group_by_date(lessons)

        for schedule_date, day_lessons in by_date.items():
            upsert_cache(cur, group["id"], "group", schedule_date, day_lessons)
            total_inserted += 1

        print(f"    → {len(by_date)} дней, {len(lessons)} пар")
        conn.commit()
        time.sleep(0.3)   # не долбим API

    # ── Преподаватели ────────────────────────────────
    print("\n👨‍🏫 Загружаем расписание преподавателей...")
    for teacher in TEACHERS:
        print(f"  Преподаватель {teacher['name']} (id={teacher['id']})...")
        lessons = fetch_schedule("person", teacher["id"])
        by_date = group_by_date(lessons)

        for schedule_date, day_lessons in by_date.items():
            upsert_cache(cur, teacher["id"], "teacher", schedule_date, day_lessons)
            total_inserted += 1

        print(f"    → {len(by_date)} дней, {len(lessons)} пар")
        conn.commit()
        time.sleep(0.3)

    # ── Аудитории ────────────────────────────────────
    print("\n🏛 Загружаем расписание аудиторий...")
    for auditory in AUDITORIES:
        print(f"  Аудитория {auditory['name']} (id={auditory['id']})...")
        lessons = fetch_schedule("auditorium", auditory["id"])
        by_date = group_by_date(lessons)

        for schedule_date, day_lessons in by_date.items():
            upsert_cache(cur, auditory["id"], "auditory", schedule_date, day_lessons)
            total_inserted += 1

        print(f"    → {len(by_date)} дней, {len(lessons)} пар")
        conn.commit()
        time.sleep(0.3)

    cur.close()
    conn.close()

    print(f"\n{'='*50}")
    print(f"✅ Готово! Вставлено записей в schedule_cache: {total_inserted}")
    print(f"{'='*50}")


if __name__ == "__main__":
    seed()