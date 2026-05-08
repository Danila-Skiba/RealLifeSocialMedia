FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TZ=Asia/Omsk

COPY parser/crontab /etc/cron.d/news-parser
RUN chmod 0644 /etc/cron.d/news-parser && crontab /etc/cron.d/news-parser

CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8000"]