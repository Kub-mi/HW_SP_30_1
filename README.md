# Домашнее задание: DRF (HW_SP_30_1)

## 📋 Описание
Учебный проект на **Django REST Framework**.
Содержит два приложения:
- `courses` — курсы и уроки
- `users` — пользователи и платежи

Выполнены задания 1–4:
1. В сериализаторе курса поле `lessons_count` через `SerializerMethodField`.
2. Новая модель `Payment` в `users` + наполнение данными (фикстура / кастомная команда).
3. В сериализаторе курса добавлен список связанных уроков.
4. Для эндпоинта платежей настроена фильтрация и сортировка.

---

## 🚀 Запуск через Docker Compose

1. Скопируйте шаблон переменных окружения и заполните нужные значения:
   ```bash
   cp .env.example .env
   ```

2. Поднимите весь стек сервисов (бэкенд, PostgreSQL, Redis, Celery worker и Celery Beat):
   ```bash
   docker compose up --build
   ```
   По умолчанию Django будет доступен на `http://localhost:8000`.

3. После первого запуска проверьте, что все сервисы работают:
   - **Бэкенд** — откройте `http://localhost:8000/api/schema/swagger-ui/` или выполните запрос:
     ```bash
     curl http://localhost:8000/api/v1/courses/
     ```
   - **PostgreSQL** — проверьте подключение и список баз данных:
     ```bash
     docker compose exec db psql -U "$DB_USER" -d "$DB_NAME" -c '\l'
     ```
   - **Redis** — выполните ping:
     ```bash
     docker compose exec redis redis-cli ping
     ```
   - **Celery worker** — посмотрите активные логи:
     ```bash
     docker compose logs celery
     ```
   - **Celery Beat** — убедитесь, что планировщик запустился:
     ```bash
     docker compose logs celery_beat
     ```

4. Остановить и удалить контейнеры можно командой:
   ```bash
   docker compose down -v
   ```

---

## ⚙️ Локальная установка без Docker

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/Kub-mi/HW_SP_30_1.git
   cd HW_SP_30_1
   ```

2. Создать и активировать виртуальное окружение:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   ```

3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Выполнить миграции:
   ```bash
   python manage.py migrate
   ```

5. Создать суперпользователя (для входа в админку):
   ```bash
   python manage.py createsuperuser
   ```

6. Запустить сервер разработки:
   ```bash
   python manage.py runserver
   ```

---

## 📂 Данные (Задание 2)

### Вариант A: загрузка через фикстуры
Файл: `users/fixtures/payments.json`

```bash
python manage.py loaddata users/fixtures/payments.json
```

### Вариант B: кастомная команда
```bash
python manage.py seed_payments
```

---

## 🔗 Эндпоинты API

### Users
- `GET /api/v1/users/` — список пользователей
- `GET /api/v1/users/{id}/` — профиль пользователя

### Courses
- `GET /api/v1/courses/` — список курсов (есть `lessons_count`)
- `GET /api/v1/courses/{id}/` — детальный курс (есть `lessons_count` + список `lessons`)

### Lessons
- `GET /api/v1/lessons/` — список уроков
- `POST /api/v1/lessons/create/` — создать урок
- `GET /api/v1/lessons/{id}/` — детальный урок
- `PUT/PATCH /api/v1/lessons/{id}/update/` — обновить урок
- `DELETE /api/v1/lessons/{id}/delete/` — удалить урок

### Payments
- `GET /api/v1/payments/` — список платежей
  - фильтрация:
    - `?course=1`
    - `?lesson=3`
    - `?method=cash`
  - сортировка:
    - `?ordering=paid_at`
    - `?ordering=-paid_at`
- `POST /api/v1/payments/create/` — создать платеж
- `GET /api/v1/payments/{id}/` — детальный платеж
- `PUT/PATCH /api/v1/payments/{id}/update/` — обновить платеж
- `DELETE /api/v1/payments/{id}/delete/` — удалить платеж

---

## 🛠 Технологии
- Python 3.13
- Django 5.2.x
- Django REST Framework
- django-filter
- PostgreSQL (можно заменить на SQLite для тестов)

---

## ☁️ Продовый сервер и деплой

### 1. Подготовьте удалённый сервер
- Создайте пользователя без привилегий `sudo adduser deploy && usermod -aG sudo deploy`.
- Включите авторизацию по SSH-ключам: скопируйте публичный ключ на сервер `ssh-copy-id deploy@<SERVER_IP>` и отключите парольный вход в `/etc/ssh/sshd_config` (`PasswordAuthentication no`).
- Обновите систему и установите базовые пакеты:
  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y python3 python3-venv python3-pip git nginx postgresql postgresql-contrib redis-server
  ```
- Настройте firewall, оставив только нужные порты (например, 22/80/443):
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 'Nginx Full'
  sudo ufw enable
  ```

### 2. Создайте инфраструктуру проекта
- Настройте базу данных PostgreSQL:
  ```sql
  sudo -u postgres psql
  CREATE DATABASE hw_sp_30_1;
  CREATE USER hw_sp WITH PASSWORD 'strong_password';
  ALTER ROLE hw_sp SET client_encoding TO 'utf8';
  ALTER ROLE hw_sp SET default_transaction_isolation TO 'read committed';
  ALTER ROLE hw_sp SET timezone TO 'UTC';
  GRANT ALL PRIVILEGES ON DATABASE hw_sp_30_1 TO hw_sp;
  \q
  ```
- Создайте структуру каталогов и клон репозитория:
  ```bash
  sudo mkdir -p /srv/hw_sp_30_1
  sudo chown deploy:deploy /srv/hw_sp_30_1
  cd /srv/hw_sp_30_1
  git clone git@github.com:Kub-mi/HW_SP_30_1.git app
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r app/requirements.txt
  ```
- Скопируйте шаблон `.env` и заполните чувствительные данные:
  ```bash
  cd /srv/hw_sp_30_1/app
  cp .env.example .env
  nano .env  # заполните секретный ключ, параметры БД, Stripe и т.д.
  ```
- Выполните подготовительные команды:
  ```bash
  source /srv/hw_sp_30_1/venv/bin/activate
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  ```

### 3. Настройте systemd и Gunicorn
- Используйте шаблон `infra/hw_sp_30_1.service` и отредактируйте пути при необходимости:
  ```bash
  sudo cp infra/hw_sp_30_1.service /etc/systemd/system/hw_sp_30_1.service
  sudo mkdir -p /var/log/hw_sp_30_1
  sudo chown www-data:www-data /var/log/hw_sp_30_1
  sudo systemctl daemon-reload
  sudo systemctl enable hw_sp_30_1.service
  sudo systemctl start hw_sp_30_1.service
  sudo systemctl status hw_sp_30_1.service
  ```
- Убедитесь, что Gunicorn слушает порт `8000`. Перезапуск произойдёт автоматически при деплое через GitHub Actions.

### 4. Настройте Nginx
- Скопируйте шаблон `infra/nginx.conf` и укажите свой домен/IP:
  ```bash
  sudo cp infra/nginx.conf /etc/nginx/sites-available/hw_sp_30_1
  sudo ln -s /etc/nginx/sites-available/hw_sp_30_1 /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx
  ```
- Для HTTPS подключите Certbot или другой инструмент по инструкции официальной документации Nginx/Let's Encrypt.

### 5. Автоматический рестарт Celery (опционально)
Если используете Celery, настройте отдельные сервисы `systemd` для worker и beat, аналогично Gunicorn.

---

## 🤖 GitHub Actions: CI/CD

Workflow находится в `.github/workflows/ci_cd.yml` и запускается при каждом `push`.

### Job `tests`
- Устанавливает Python 3.12 и зависимости из `requirements.txt`.
- Прогоняет миграции и выполняет `python manage.py test` на SQLite.
- При падении тестов деплой не запускается.

### Job `deploy`
- Запускается только для ветки `develop`, если тесты завершились успешно.
- Подключается к серверу по SSH (используется секретный ключ) и выполняет скрипт `deploy/deploy.sh`.
- Скрипт перезапускает systemd-сервис, поэтому приложение обновляется автоматически.

### Секреты, которые нужно добавить в настройках репозитория
| Имя секрета | Назначение |
|-------------|------------|
| `DEPLOY_SSH_KEY` | Закрытый SSH-ключ с доступом к пользователю на сервере |
| `DEPLOY_HOST` | Домен или IP удалённого сервера |
| `DEPLOY_USER` | Пользователь на сервере (например, `deploy`) |
| `DEPLOY_APP_DIR` | Путь к каталогу приложения (`/srv/hw_sp_30_1/app`) |
| `DEPLOY_VENV_PATH` | Путь к виртуальному окружению (`/srv/hw_sp_30_1/venv`) |
| `DEPLOY_SERVICE_NAME` | Имя systemd-сервиса (по умолчанию `hw_sp_30_1`) |
| `DEPLOY_ENV_FILE` | (Опционально) путь до `.env`, если отличается от `APP_DIR/.env` |

Добавьте публичный ключ, соответствующий `DEPLOY_SSH_KEY`, в файл `~/.ssh/authorized_keys` на сервере.

---

## 📦 Шаблон переменных окружения

Файл `.env.example` содержит минимальный набор переменных для продакшена и локального запуска. Скопируйте его в `.env` и заполните значения перед деплоем или запуском через Docker Compose.
