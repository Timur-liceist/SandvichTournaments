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
# Добавляем gunicorn, если его вдруг нет в requirements.txt, но лучше добавить туда
RUN pip install --no-cache-dir --index-url=https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем необходимые папки заранее
RUN mkdir -p /home/app/django_project/logs \
    && mkdir -p /home/app/django_project/staticfiles \
    && mkdir -p /home/app/django_project/media

# Назначаем владельца
RUN chown -R app:app /home/app

USER app

EXPOSE 8000

# CMD оставляем пустым или дефолтным, так как docker-compose его переопределит
# Но для локального запуска без compose можно оставить:
CMD ["sh", "-c", "python django_project/manage.py migrate && gunicorn django_project.django_project.wsgi:application --bind 0.0.0.0:8000"]