## Добро пожаловать в мой репозиторий :)

Позже здесь будет проект-дз...

### О себе

Я интересуюсь **backend-разработкой**, **серверными инструментами** и **микроконтроллерами**.
Пишу на Java, Python и C++, начинал с написания плагинов для Minecraft и разных полезных утилит.

🔧 Студент VK Education, курса "Web-разработка".


## Запуск проекта
Перед запуском нужно составить корректный .env файл! Можно использовать .env.example!

### На текущей машине

```shell
python manage.py runserver 8000
pip install --no-cache-dir -r requirements.txt
```

### Docker

ВАЖНО! Использовать .env.docker вместо .env.example в качестве образца!

```shell
docker compose up --build
```

Запустится именно на 127.0.0.1:8000


## Миграции и заполнение дб

Заполнить ДБ 10000 рандомных данных

```
python manage.py makemigrations
python manage.py migrate
python manage.py fill_db 10000
```