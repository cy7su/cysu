# Multi-stage build для оптимизации размера образа

# Builder stage - для установки зависимостей
FROM python:3.11-alpine AS builder

# Устанавливаем системные зависимости для компиляции
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    postgresql-dev

# Создаем виртуальное окружение
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-alpine

# Устанавливаем timezone и locale
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
    echo "Europe/Moscow" > /etc/timezone

# Создаем пользователя для безопасности
RUN addgroup -g 1000 -S appuser && \
    adduser -u 1000 -S appuser -G appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем виртуальное окружение из builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем код приложения (исключая ненужные файлы)
COPY --chown=appuser:appuser . .

# Создаем необходимые директории с правильными правами
RUN mkdir -p app/static/uploads app/static/ticket_files logs && \
    chown -R appuser:appuser app/static/uploads app/static/ticket_files logs

# Переключаемся на пользователя без root прав
USER appuser

# Устанавливаем переменные окружения
ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    TZ=Europe/Moscow

# Открываем порт
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "
try:
    import requests
    response = requests.get('http://localhost:8001', timeout=10)
    exit(0 if response.status_code > 0 else 1)
except:
    exit(1)
" || exit 1

# Команда запуска
CMD ["python", "run.py"]
