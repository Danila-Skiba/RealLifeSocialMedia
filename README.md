## Лабораторная работа №1

### Ветки (branches):

1. **init/setup** – Инициализация проекта

2. **features/main-server** – Разработка основого сервера

3. **feature/websocket-service** - WebSocket сервис

4. **feature/client-server** – Клиентский сервер

5. **feature/client-websocket** – Клиентская WebSocket логика

6. **integration/link-servers** – Связывание серверов

7. **infrastructure/reverse-proxy** – Настройка инфраструктуры

8. **integration/domain-migration** – Переход на доменные имена

9. **testing/deployment** – Тестирование и деплой

10. **documentation/final** – Финальная документация

#### Ветка **init/setup**

1. Определится со стеком:
    - **Backend**: Python + FastAPI, 
    - **BD**: PostgreSQL, 
    - **ORM**: SQLAlchemy, 
    - **HTML генерация**: htpy, 
    - **ASGI сервер**: uvicorn.

2. Структура проекта: 

theme-project/           
    ├── client/              # Клиентский сервер
    ├── server/              # Основной сервер
    ├── docs/                # Документация
    ├── scripts/             # Вспомогательные скрипты
    ├── requirements.txt            
├── .gitignore       
├── README.md   

venv/   

3. Создать виртуальное окружение ```Python```

4. Cформировать файл ```requirements.txt``` 

5. Настроить ```.gitignore``` (исключить папку с виртуальным окружением)