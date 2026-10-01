FROM python:3.12-slim

WORKDIR /app

COPY services/identity/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY services/identity/app ./app

COPY database/identity/migrations ./database/identity/migrations

COPY services/identity/tests ./tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]