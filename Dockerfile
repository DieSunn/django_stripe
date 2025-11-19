FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Сбор статики
RUN SECRET_KEY=building_secret_key \
    STRIPE_PUBLIC_KEY=pk_test_build \
    STRIPE_SECRET_KEY=sk_test_build \
    ALLOWED_HOSTS=127.0.0.1,localhost \
    DEBUG=True \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]