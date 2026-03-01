FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

# Создаём пользователя
RUN useradd --create-home --shell /bin/bash app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё
COPY . .

# Гарантируем существование папки logs
RUN mkdir -p /home/app/django_project/logs

# Назначаем владельца
RUN chown -R app:app /home/app

USER app

EXPOSE 8000

CMD ["sh", "-c", "python django_project/manage.py migrate && python django_project/manage.py runserver 0.0.0.0:8000"]