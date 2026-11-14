# Используем официальный образ Python 3.12 (slim-версия, чтобы образ был меньше)
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY Pipfile Pipfile.lock ./

# Устанавливаем pipenv и зависимости из Pipfile.lock
RUN pip install --no-cache-dir pipenv && \
    pipenv sync --system

# Копируем всё остальное содержимое проекта в контейнер
COPY . .

# Открываем порт, который будет слушать uvicorn (внутри контейнера)
EXPOSE 8000

# Команда для запуска приложения.
# Важно: используем $PORT, чтобы Render мог назначить свой порт.
CMD pipenv run uvicorn fastlab:app --host 0.0.0.0 --port ${PORT:-8000}