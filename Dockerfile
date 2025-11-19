FROM python:3.11-slim

WORKDIR /app

# install build deps and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "weather_service.frontend.app:app", "--host", "0.0.0.0", "--port", "8000"]
