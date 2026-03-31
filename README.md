# 🛍️ Store Server

Django интернет-магазин с полным функционалом электронной коммерции.

---

## ✨ Функциональность

### 🎯 Основные возможности
- Каталог товаров - категории, фильтрация, поиск
- Корзина покупок - добавление/удаление товаров
- Аутентификация - регистрация, вход, верификация email
- Восстановление пароля - полный цикл сброса через email
- Онлайн-платежи - интеграция с Stripe
- Управление заказами - история заказов, статусы
- Email уведомления - различные типы уведомлений
- Админ-панель - полное управление магазином

### 🛠 Технические особенности
- **Redis** - кэширование, сессии и брокер для Celery
- **PostgreSQL** - основная база данных
- **Stripe API** - обработка платежей
- **Django-Allauth** - система аутентификации с подтверждением email
- **Celery** - асинхронная отправка email
- **Django Debug Toolbar** - отладка разработки

---

## 🚀 Быстрый старт

### 📋 Требования
- Docker и Docker Compose
- Python 3.13+ (для локальной установки)
- PostgreSQL (для локальной установки)
- Redis (для локальной установки)

---

## Запуск через Docker

### 1. Настроить окружение
Отредактируйте `.env`:

`DATABASE_HOST=db`
`REDIS_HOST=redis`

### 2. Запустить контейнеры
`docker-compose up --build`

### 3. Применить миграции
`docker-compose exec web python manage.py migrate`

### 4. Загрузить фикстуры
`docker-compose exec web python manage.py loaddata products/fixtures/categories.json`

`docker-compose exec web python manage.py loaddata products/fixtures/goods.json`

### 5. Создать суперпользователя
`docker-compose exec web python manage.py createsuperuser`

### 6. Открыть в браузере
Сайт: `http://localhost:8000`

Админ-панель: `http://localhost:8000/admin`