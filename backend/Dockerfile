FROM python:3.13-slim


ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PYTHONPATH=/backend

# Устанавливаем рабочую директорию
WORKDIR /backend


RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ----------- Создаём пользователя -----------
ARG user=django-user
RUN adduser --disabled-password --gecos "" $user
USER $user

# Добавляем pip local path
ENV PATH="/home/$user/.local/bin:$PATH"

# ----------- Копируем зависимости и .env -----------
COPY --chown=$user:$user requirements.txt ./
COPY --chown=$user:$user .env ./

# Устанавливаем зависимости
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# ----------- Копируем проект -----------
COPY --chown=$user:$user . /backend

# ----------- Открываем порт -----------
EXPOSE 8000

# ----------- Запуск -----------
CMD ["uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--workers", "3", "--log-level", "info"]