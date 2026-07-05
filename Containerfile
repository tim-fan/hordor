FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements_lock.txt ./
RUN pip install --no-cache-dir -r requirements_lock.txt

COPY hordor/ ./hordor/
WORKDIR /app/hordor

EXPOSE 8000

# collectstatic needs real settings (SECRET_KEY, HORDOR_DOMAIN) from the
# environment, so it runs at container start rather than at build time --
# migrations are deliberately NOT run here, since every schema change in this
# app is verified against an isolated DB copy first and applied manually.
CMD ["sh", "-c", "python manage.py collectstatic --noinput && exec gunicorn hordor.wsgi:application --bind 0.0.0.0:8000"]
