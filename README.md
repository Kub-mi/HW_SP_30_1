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

## ⚙️ Установка и запуск

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
