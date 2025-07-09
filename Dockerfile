FROM python:3.11-slim

WORKDIR /app

COPY src/bot/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN mkdir -p /app/logs

CMD ["python", "src/bot/main.py"] 