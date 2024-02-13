# Use the official Streamlit image as the base image
FROM python:3.11-slim 

# Copy the Streamlit app into the Docker image
WORKDIR /app/tenant

COPY jb-tenant/pyproject.toml jb-tenant/poetry.lock jb-tenant/README.md ./
COPY jb-tenant/jugalbandi/tenant/__init__.py ./

RUN pip install poetry

RUN poetry config virtualenvs.create false && \
  poetry install --no-root --no-dev

COPY jb-tenant/jugalbandi/tenant/ ./

EXPOSE 8080

CMD ["streamlit", "run", "--server.port", "8080", "streamlitapp.py"]
