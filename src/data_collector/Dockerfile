FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://flaskuser:flaskpass@my_flask_app_db:5432/flaskdb

CMD ["python", "-m", "src.data_collector"]
