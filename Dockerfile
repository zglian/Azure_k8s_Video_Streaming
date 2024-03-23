FROM python:3.11
WORKDIR /app
COPY backend /app/backend
COPY pyproject.toml poetry.lock ./

RUN pip install poetry 
RUN poetry install

WORKDIR /app/backend
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]