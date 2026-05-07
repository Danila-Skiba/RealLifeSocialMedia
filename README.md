# Архитектура omstu-backend

## Предметная область

Мобильное приложение расписания ОмГТУ. Функционал: просмотр расписания, новости университета, ведение конспектов лекций с помощью ИИ, личные задачи студента.

---

## Микросервисы

### 1. Gateway
**Роль:** Единая точка входа для мобильного клиента. Принимает все запросы от Flutter, маршрутизирует их в нужный сервис. Проверяет JWT токен для защищённых эндпоинтов, не пропуская неавторизованные запросы дальше.

| Вызов микросервиса | Внешние вызовы |
|---|---|
| `GET /api/news` | news-service. `GET /news` |
| `GET /api/news/images/{id}` | news-service. `GET /news/images/{id}` |
| `POST /api/auth/register` | auth-service. `POST /auth/register` |
| `POST /api/auth/login` | auth-service. `POST /auth/login` |
| `GET /api/auth/me` | auth-service. `GET /auth/me` |
| `GET /api/schedule/{group_id}` | schedule-service. `GET /schedule/{group_id}` |
| `GET /api/schedule/teacher/{id}` | schedule-service. `GET /schedule/teacher/{id}` |
| `POST /api/tasks` | schedule-service. `POST /tasks` |
| `GET /api/tasks` | schedule-service. `GET /tasks` |
| `DELETE /api/tasks/{id}` | schedule-service. `DELETE /tasks/{id}` |
| `POST /api/lectures/session` | lecture-service. `POST /session` |
| `POST /api/lectures/session/{id}/photo` | lecture-service. `POST /session/{id}/photo` |
| `POST /api/lectures/session/{id}/compile` | lecture-service. `POST /session/{id}/compile` |
| `GET /api/lectures` | lecture-service. `GET /lectures` |
| `DELETE /api/lectures/session/{id}` | lecture-service. `DELETE /session/{id}` |

**Внутренние вызовы:**
- auth-service. `GET /auth/validate` — проверка JWT перед проксированием защищённых маршрутов `/api/tasks/*`, `/api/lectures/*`

**Зависимости от БД:** нет

---

### 2. Auth Service
**Роль:** Управление пользователями и авторизацией. Регистрирует студентов, выдаёт JWT токены при логине, валидирует токены по запросу от других сервисов.

| Вызов микросервиса | Зависимость от БД | Внешние вызовы |
|---|---|---|
| `POST /auth/register` | INSERT → `users` | — |
| `POST /auth/login` | SELECT → `users` | — |
| `GET /auth/me` | SELECT → `users` | — |
| `GET /auth/validate` *(внутренний)* | SELECT → `users` | — |

**Таблицы БД:**
```
users
  id          UUID PRIMARY KEY
  email       VARCHAR UNIQUE NOT NULL
  password    VARCHAR NOT NULL        -- bcrypt hash
  name        VARCHAR
  created_at  TIMESTAMP
```

**Зависимости от других сервисов:** нет — auth-service независим

---

### 3. News Service
**Роль:** Отдаёт новости университета и изображения к ним. Скрипт парсит сайт ОмГТУ раз в сутки и сохраняет в файловое хранилище. News-service только читает файлы и отдаёт клиенту. БД не используется — хранилище файловое.

| Вызов микросервиса | Зависимость от БД | Внешние вызовы |
|---|---|---|
| `GET /news` | — (читает `data/news.json`) | — |
| `GET /news/images/{id}` | — (читает `data/images/{id}/image.jpg`) | — |

**Файловое хранилище:**
```
data/
  news.json          -- [{id, title, date, url, image}, ...]
  images/
    {news_id}/
      image.jpg
```

**Зависимости от других сервисов:** нет — данные поставляет Airflow через общую папку `data/`

---

### 4. Schedule Service
**Роль:** Предоставляет расписание групп и преподавателей. Реализует TTL-кэш — при первом запросе группы идёт в официальное API ОмГТУ, сохраняет результат в БД. Повторные запросы в течение 2 часов отдаются из БД без обращения к внешнему API. Также хранит личные задачи студентов (дедлайны, напоминания).

| Вызов микросервиса | Зависимость от БД | Внешние вызовы |
|---|---|---|
| `GET /schedule/group/{id}` | SELECT/INSERT → `schedule_cache` | API ОмГТУ (если кэш устарел) |
| `GET /schedule/teacher/{id}` | SELECT/INSERT → `schedule_cache` | API ОмГТУ (если кэш устарел) |
| `GET /schedule/auditory/{id}` | SELECT/INSERT → `schedule_cache` | API ОмГТУ (если кэш устарел) |
| `POST /tasks` | INSERT → `personal_tasks` | — |
| `GET /tasks` | SELECT → `personal_tasks` | — |
| `DELETE /tasks/{id}` | DELETE → `personal_tasks` | — |

**Таблицы БД:**
```
schedule_cache
  id          UUID PRIMARY KEY
  entity_id   VARCHAR NOT NULL    -- group_id или teacher_id
  entity_type VARCHAR NOT NULL    -- 'group' или 'teacher'
  data        JSONB NOT NULL      -- расписание от API ОмГТУ
  fetched_at  TIMESTAMP NOT NULL  -- время последнего обновления

personal_tasks
  id          UUID PRIMARY KEY
  user_id     UUID NOT NULL       -- из auth-service (не FK)
  title       VARCHAR NOT NULL
  description TEXT
  deadline    TIMESTAMP
  group_id    VARCHAR             -- к какой группе привязана
  created_at  TIMESTAMP
```

**Внутренние вызовы:** нет
**Зависимости от других сервисов:** `user_id` берётся из JWT токена, валидированного gateway

---

### 5. Lecture Service
**Роль:** Управляет сессиями ведения конспектов. Студент создаёт сессию, загружает фото с доски — сервис отправляет их в GigaChat, получает распознанный текст с LaTeX формулами и сохраняет как фрагмент. По команде компилирует все фрагменты в единый Markdown файл через повторный запрос к GigaChat. Требует авторизации для всех эндпоинтов.

| Вызов микросервиса | Зависимость от БД | Внешние вызовы |
|---|---|---|
| `POST /session` | INSERT → `sessions` | auth-service. `GET /auth/validate` |
| `POST /session/{id}/photo` | INSERT → `fragments` | auth-service. `GET /auth/validate`, GigaChat API |
| `POST /session/{id}/compile` | SELECT → `fragments`, UPDATE → `sessions` | auth-service. `GET /auth/validate`, GigaChat API |
| `GET /lectures` | SELECT → `sessions` | auth-service. `GET /auth/validate` |
| `GET /session/{id}` | SELECT → `sessions`, `fragments` | auth-service. `GET /auth/validate` |
| `DELETE /session/{id}` | DELETE → `sessions`, `fragments` | auth-service. `GET /auth/validate` |

**Таблицы БД:**
```
sessions
  id            UUID PRIMARY KEY
  user_id       UUID NOT NULL       -- из auth-service (не FK)
  subject       VARCHAR NOT NULL    -- название дисциплины
  created_at    TIMESTAMP
  compiled_at   TIMESTAMP           -- NULL если ещё не компилировали
  md_path       VARCHAR             -- путь к готовому .md файлу

fragments
  id            UUID PRIMARY KEY
  session_id    UUID NOT NULL REFERENCES sessions(id)
  index         INTEGER NOT NULL    -- порядок фрагмента
  markdown_text TEXT NOT NULL       -- распознанный текст от GigaChat
  gigachat_file_id VARCHAR          -- ID файла в хранилище GigaChat
  created_at    TIMESTAMP
```

**Внутренние вызовы (вызываются другими сервисами):** нет — lecture-service конечный
**Зависимости от других сервисов:** auth-service для валидации токена на каждом эндпоинте

---

## Схема взаимодействия

```
Flutter App
     │
     ▼
 Gateway :8000
     │
     ├──────────────────────────────────────────┐
     │                                          │
     │  Проверка JWT (защищённые маршруты)      │
     │  ◄──── auth-service :8002 ──────────►   │
     │                                          │
     ├── /api/news/*       ──► news-service :8001
     │
     ├── /api/auth/*       ──► auth-service :8002
     │
     ├── /api/schedule/*   ──► schedule-service :8003
     │                              │
     │                              └──► API ОмГТУ (внешний)
     │
     └── /api/lectures/*   ──► lecture-service :8004
                                      │
                                      ├──► auth-service :8002
                                      └──► GigaChat API (внешний)
```

---

## Открытые и защищённые маршруты

| Маршрут | Авторизация |
|---|---|
| `GET /api/news` | ✅ открытый |
| `GET /api/news/images/{id}` | ✅ открытый |
| `POST /api/auth/register` | ✅ открытый |
| `POST /api/auth/login` | ✅ открытый |
| `GET /api/schedule/group/{id}` | ✅ открытый |
| `GET /api/schedule/teacher/{id}` | ✅ открытый |
| `GET /api/schedule/auditory/{id}` | ✅ открытый |
| `GET /api/tasks` | 🔒 JWT required |
| `POST /api/tasks` | 🔒 JWT required |
| `DELETE /api/tasks/{id}` | 🔒 JWT required |
| `ALL /api/lectures/*` | 🔒 JWT required |

---

## Стек технологий

| Компонент | Технология |
|---|---|
| Язык | Python 3.11 |
| Web-фреймворк | FastAPI |
| ORM | SQLAlchemy 2.0 |
| БД | PostgreSQL 15 |
| Контейнеризация | Docker + docker-compose |
| ИИ | GigaChat API (vision) |
| Авторизация | JWT (python-jose) |
| Хэширование паролей | bcrypt |
| Бинарный протокол | MessagePack |
| RPC | gRPC |