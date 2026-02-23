FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Build-time SECRET_KEY (only used during build for collectstatic)
# Production deployments MUST override this via runtime environment variable
ARG BUILD_SECRET_KEY=build-time-secret-key-not-for-production
ENV SECRET_KEY=${BUILD_SECRET_KEY}

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
