import psycopg2
import random
from faker import Faker
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': 'localhost',
    'database': 'omstu_db',
    'user': 'omstu',
    'password': 'omstu', 
    'port': 5430,
}

fake = Faker("ru_RU")

SUBJECTS = [
    "Математический анализ",
    "Линейная алгебра",
    "Численные методы",
    "Теория вероятностей",
    "Физика",
    "Программирование на Python",
    "Базы данных",
    "Операционные системы",
    "Компьютерные сети",
    "Алгоритмы и структуры данных",
]

FRAGMENT_TEMPLATES = [
    """## {topic}

Основное определение: рассматривается понятие {concept}, которое играет ключевую роль в данном разделе.

Формула: $$f(x) = \\sum_{{i=0}}^{{n}} a_i x^i$$

Свойства:
- Линейность: $f(ax + by) = af(x) + bf(y)$
- Непрерывность в точке $x_0$
- Дифференцируемость на интервале $(a, b)$
""",
    """## Теорема о {concept}

**Формулировка:** Если функция $f(x)$ непрерывна на $[a, b]$, то:

$$\\int_a^b f(x)dx = F(b) - F(a)$$

где $F(x)$ — первообразная функции $f(x)$.

**Доказательство:** следует из определения интеграла Римана.
""",
    """## Метод {concept}

Алгоритм:
1. Задаём начальное приближение $x_0$
2. На каждом шаге вычисляем $x_{{n+1}} = x_n - \\frac{{f(x_n)}}{{f'(x_n)}}$
3. Останавливаемся при $|x_{{n+1}} - x_n| < \\varepsilon$

Погрешность метода: $|\\Delta x| \\leq \\frac{{M_2}}{{2m_1}}|x_{{n+1}} - x_n|^2$
""",
    """## Определение {concept}

Пусть задано множество $X$ и отображение $f: X \\to Y$.

Говорят, что $f$ является **{concept}**, если выполняются условия:
- $\\forall x \\in X: f(x) \\in Y$
- $f(x_1) = f(x_2) \\Rightarrow x_1 = x_2$

Примеры: линейные операторы, матричные преобразования.
""",
]

CONCEPTS = [
    "производной", "интеграла", "предела", "матрицы", "вектора",
    "собственных значений", "нормы", "метрики", "топологии", "группы",
    "Ньютона", "Лагранжа", "Эйлера", "Гаусса", "Рунге-Кутта",
]

TOPICS = [
    "Введение", "Основные понятия", "Теоремы", "Методы решения",
    "Практические задачи", "Примеры", "Итог лекции",
]


def random_fragment_text() -> str:
    template = random.choice(FRAGMENT_TEMPLATES)
    return template.format(
        topic=random.choice(TOPICS),
        concept=random.choice(CONCEPTS),
    )


def random_date_past(days: int = 180) -> datetime:
    return datetime.now() - timedelta(days=random.randint(0, days))


def seed_sessions_and_fragments(sessions_count: int = 100):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Получаем user_id из таблицы users
    cur.execute("SELECT id FROM users LIMIT 200;")
    user_ids = [row[0] for row in cur.fetchall()]

    print(f"Найдено {len(user_ids)} пользователей")

    sessions_inserted = 0
    fragments_inserted = 0

    for i in range(sessions_count):
        user_id = random.choice(user_ids)
        subject = random.choice(SUBJECTS)
        created_at = random_date_past(180)
        is_compiled = random.random() > 0.3   # 70% сессий скомпилированы

        # Генерируем фрагменты
        fragments_count = random.randint(2, 6)
        fragments_texts = [random_fragment_text() for _ in range(fragments_count)]

        # md_content для скомпилированных сессий
        md_content = None
        compiled_at = None
        if is_compiled:
            compiled_at = created_at + timedelta(hours=random.randint(1, 3))
            md_content = f"# {subject}\n\n" + "\n\n---\n\n".join(fragments_texts) + \
                         f"\n\n## Ключевые формулы\n\n- Основная формула темы\n\n## Итог\n\n- Рассмотрены основные понятия по теме {subject}\n"

        # Вставляем сессию
        cur.execute(
            """
            INSERT INTO sessions (user_id, subject, created_at, compiled_at, md_content)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (str(user_id), subject, created_at, compiled_at, md_content)
        )
        session_id = cur.fetchone()[0]
        sessions_inserted += 1

        # Вставляем фрагменты только для незавершённых сессий
        # (скомпилированные уже почищены по логике приложения)
        if not is_compiled:
            for idx, text in enumerate(fragments_texts):
                fragment_created_at = created_at + timedelta(minutes=idx * 10)
                cur.execute(
                    """
                    INSERT INTO fragments (session_id, index, markdown_text, gigachat_file_id, created_at)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        str(session_id),
                        idx + 1,
                        text,
                        f"gigachat_file_{fake.uuid4()}",
                        fragment_created_at,
                    )
                )
                fragments_inserted += 1

        conn.commit()
        print(f"[{sessions_inserted:>3}/100] Сессия: {subject} — {'скомпилирована' if is_compiled else f'{fragments_count} фрагментов'}")

    cur.close()
    conn.close()
    print(f"\nГотово!")
    print(f"Сессий вставлено:   {sessions_inserted}")
    print(f"Фрагментов вставлено: {fragments_inserted}")


if __name__ == "__main__":
    seed_sessions_and_fragments(100)