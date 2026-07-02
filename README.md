# Docs QA Backend

Веб-сервис для вопросов-ответов по документам (RAG). Загружаешь PDF — сервис
разбивает его на чанки, кладёт эмбеддинги в векторную БД и отвечает на вопросы
по содержимому через LLM.

## Стек

- **API** — FastAPI + Uvicorn
- **LLM** — OpenRouter (`owl-alpha`) через `langchain-openrouter`
- **Эмбеддинги** — HuggingFace `sentence-transformers/all-mpnet-base-v2` (локально)
- **Векторная БД** — PostgreSQL + pgvector (`langchain-postgres`), в Docker
- **Оркестрация** — langchain agent + `@dynamic_prompt` middleware
- **Парсинг PDF** — pypdf
- **Пакеты** — uv, Python 3.12

## Архитектура

Пайплайн разделён на две части:

```
Offline (индексация):
  POST /upload/ → pypdf → RecursiveCharacterTextSplitter (1000/200)
               → эмбеддинги → PGVector (коллекция "my-docs")

Online (ответы):
  POST /ask/ → agent.invoke → dynamic_prompt middleware:
               similarity_search по PGVector → контекст в system prompt
             → LLM → текст ответа клиенту
```

| Файл | Ответственность |
|------|-----------------|
| `main.py` | FastAPI-приложение, эндпоинты; `Pipeline` создаётся в lifespan |
| `utils/pipeline.py` | Класс `Pipeline`: собирает модель, эмбеддинги, БД и агента; методы `offline_pipeline` / `online_pipeline` |
| `utils/offline_part.py` | Фабрики компонентов: модель, эмбеддинги, сплиттер, подключение к PGVector, запись в БД |
| `utils/online_part.py` | `make_prompt_with_context(vector_store)` — фабрика middleware, подставляющей найденный контекст в системный промпт |
| `utils/service.py` | Извлечение текста из PDF / Markdown |
| `config.py` | Загрузка переменных окружения из `.env` |

## Запуск

### 1. Требования

- Docker (для Postgres + pgvector)
- uv
- API-ключ OpenRouter

### 2. Настройка

Создай `.env` в корне проекта:

```
OPENROUTER_API_KEY=sk-or-...
```

Убедись, что порт `5432` на хосте свободен (частая проблема — нативный
Postgres на Windows уже занял его; проверка: `netstat -ano | findstr :5432`).

### 3. Поднять БД

```bash
docker compose up -d
```

Поднимает `pgvector/pgvector` (Postgres 18) с базой `example_db` на
`localhost:5432`. Схему создавать не нужно — PGVector сам создаёт расширение
`vector` и свои таблицы при первом подключении.

### 4. Запустить сервис

```bash
uv sync
uv run uvicorn main:app --reload
```

Первый запуск скачивает модель эмбеддингов (~400 MB). Сервис доступен на
`http://127.0.0.1:8000`, интерактивная документация — на `/docs` (Swagger).

## API

### `POST /upload/`

Загрузка PDF в базу знаний. Файл сохраняется в `data/`, индексируется и
добавляется в векторное хранилище.

- Тело: `multipart/form-data`, поле `file`
- Поддерживается только `application/pdf`, иначе `400`

```bash
curl -X POST http://127.0.0.1:8000/upload/ -F "file=@document.pdf"
```

### `POST /ask/`

Вопрос по загруженным документам. Возвращает текст ответа модели.

- Тело: `{"user_query": "..."}`
- Пустой запрос → `400`

```bash
curl -X POST http://127.0.0.1:8000/ask/ \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What is the topic about?"}'
```

## Известные ограничения

- Индексация выполняется синхронно внутри запроса — загрузка большого PDF
  блокирует сервис.
- Обработка ошибок минимальна (нет обработки недоступности БД / LLM).
- Строка подключения к БД захардкожена в `utils/offline_part.py`.
