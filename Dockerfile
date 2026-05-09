# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar Poetry
RUN pip install poetry

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock* ./

# Instalar dependencias sin entorno virtual
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

# Copiar el código del backend
COPY app ./app

# Exponer el puerto
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]