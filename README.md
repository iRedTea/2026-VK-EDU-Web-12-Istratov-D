# 2026-VK-EDU-Web-12-Istratov-D

## Запуск в Docker

1. Скопируйте `.env.docker` в `.env` или создайте свой файл на основе `.env.example`.
2. Запустите сервисы:

```bash
docker compose up --build
```

3. Откройте приложение: `http://127.0.0.1:8080`
4. Centrifugo доступен на `http://127.0.0.1:8001`
5. Maildev доступен на `http://127.0.0.1:1080`

## Переменные окружения

В `.env` должны быть:

- `SECRET_KEY`
- `DEBUG`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_CACHE_DB`, `REDIS_BROKER_DB`, `REDIS_BEAT_DB`
- `CENTRIFUGO_URL`, `CENTRIFUGO_API_KEY`
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `DEFAULT_FROM_EMAIL`

## Миграции

После изменений моделей выполните:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Дополнительные конфигурации

- `gunicorn_conf.py` — конфигурация Gunicorn с двумя воркерами.
- `simple_wsgi.py` — простой WSGI-приложение для запуска без Django на `localhost:8081`.
- `nginx.conf` — пример конфигурации Nginx для отдачи `/uploads/`, статических файлов и проксирования на Gunicorn.

## Заполнить базу данных

```bash
python manage.py fill_db 10000
```

Когда запущено в докере:

```bash
docker compose exec python-app python manage.py fill_db 10000
```

Это удалит предыдущие данные из дб!

## Реализовано

- Redis / Celery / Celery Beat
- кэширование популярных тегов и лучших участников
- асинхронные уведомления в Centrifugo
- отправка email-уведомлений через Celery
- полнотекстовый поиск и подсказки
- Docker Compose инфраструктура

```