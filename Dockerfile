# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p app/static/uploads app/static/ticket_files logs

# Устанавливаем права на запись для директорий
RUN chmod -R 755 app/static/uploads app/static/ticket_files logs

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Открываем порт
EXPOSE 8001

# Устанавливаем переменные окружения
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Команда запуска
CMD ["python", "run.py"]
