FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api_app/ ./api_app/
COPY settings.toml .

EXPOSE 5001

CMD ["python", "-m", "api_app.run"]
