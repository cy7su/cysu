# 🎓 CYSU - Образовательная платформа

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**CYSU** - это современная веб-платформа для управления образовательным процессом, включающая систему пользователей, предметов, материалов и платежей.

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/cy7su/cysu.git
cd cysu
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
# ОСНОВНЫЕ НАСТРОЙКИ
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# БАЗА ДАННЫХ
DATABASE_URL=sqlite:///app.db
# Для PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost/cysu


# EMAIL НАСТРОЙКИ
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# YOOKASSA (ПЛАТЕЖИ)
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
YOOKASSA_TEST_MODE=True

# ЦЕНЫ ПОДПИСОК (в рублях)
SUBSCRIPTION_PRICE_1=89.00
SUBSCRIPTION_PRICE_3=199.00
SUBSCRIPTION_PRICE_6=349.00
SUBSCRIPTION_PRICE_12=469.00

# ЗАГРУЗКА ФАЙЛОВ
UPLOAD_FOLDER=app/static/uploads
TICKET_FILES_FOLDER=app/static/ticket_files
MAX_CONTENT_LENGTH=20971520  # 20MB

# ЛОГИРОВАНИЕ
LOG_FILE=logs/app.log
LOG_LEVEL=INFO
```

### 5. Инициализация базы данных
```bash
# Создание папки для логов
mkdir -p logs

# Инициализация Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Запуск приложения
```bash
python3 run.py
```

🌐 **Приложение доступно по адресу**: http://localhost:8001

## 👤 Учетные данные по умолчанию

|       Роль        |  Логин  |   Пароль   |      Email      |
|-------------------|---------|------------|-----------------|
| **Администратор** | `admin` | `admin123` | `admin@cysu.ru` |

⚠️ **Важно**: Измените пароль администратора после первого входа!


## 🛠️ Технологии

### Backend
- **Flask 3.0.2** - Веб-фреймворк
- **SQLAlchemy 2.0.23** - ORM для базы данных
- **Flask-Migrate 4.0.5** - Миграции БД
- **Flask-Login 0.6.3** - Аутентификация
- **Flask-WTF 1.2.1** - Формы и CSRF защита

### Frontend
- **Bootstrap 5** - CSS фреймворк
- **Vanilla JavaScript** - Клиентская логика
- **SVG Patterns** - Динамические фоны
- **Responsive Design** - Адаптивная верстка

### База данных
- **SQLite** (по умолчанию)
- **PostgreSQL** (поддерживается)

### Платежи
- **YooKassa** - Платежная система

## 🔧 Разработка

### Запуск в режиме разработки
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python3 run.py
```

### Создание миграции
```bash
flask db migrate -m "Описание изменений"
flask db upgrade
```

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.
