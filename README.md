## Добро пожаловать в мой репозиторий :)

Позже здесь будет проект-дз...

### О себе

Я интересуюсь **backend-разработкой**, **серверными инструментами** и **микроконтроллерами**.
Пишу на Java, Python и C++, начинал с написания плагинов для Minecraft и разных полезных утилит.

🔧 Студент VK Education, курса "Web-разработка".


## HW-1:
- создан репозиторий и подкаталоги внутри
- создана базовая структура проекта (/public/*.html, /public/static/css/style.css, /public/static/js/script.js)
- подключена библиотека bootstrap локально (/public/static/css/bootstrap.min.css) (пока не использовалась, подключена на будущее)
- настроены права (protected main branch + merge только через PR)
<img width="1240" height="1086" alt="image" src="https://github.com/user-attachments/assets/e576c646-e5e6-43dc-82a3-b130f8f7583b" />
<img width="1213" height="357" alt="image" src="https://github.com/user-attachments/assets/28d203f8-4a45-4a4b-84d2-ea4f9251bc27" />
<img width="656" height="225" alt="image" src="https://github.com/user-attachments/assets/3f714157-1b8e-4fd0-aa14-5396735c8d60" />
- настроен .gitignore (за основу взят шаблон для python)
- сверстаны base.html, index.html, question.html, ask.html, login.html, signup.html, profile.html
>>>>>>> main

## Запуск проекта

### 1. Установка корректных .env

Для отладки можно переименовать .env.example в .env

### 2. На текущей машине
```shell
pip install --no-cache-dir -r requirements.txt
python manage.py runserver 8000
```

### 2. Docker

```shell
docker compose up --build
```

Запустится именно на 127.0.0.1:8000

