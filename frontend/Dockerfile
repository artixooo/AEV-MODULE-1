FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pydantic

COPY . /app

EXPOSE 3000

ENV PORT=3000

CMD ["python", "server.py"]
