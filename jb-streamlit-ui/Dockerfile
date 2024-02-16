# Use the official Streamlit image as the base image
FROM python:3.11-slim 

# Copy the Streamlit app into the Docker image
WORKDIR /app/streamlit-ui

COPY jb-streamlit-ui/pyproject.toml jb-streamlit-ui/poetry.lock jb-streamlit-ui/README.md ./
COPY jb-streamlit-ui/jugalbandi/streamlit-ui/__init__.py ./

RUN pip install poetry

RUN poetry config virtualenvs.create false && \
  poetry install --no-root --no-dev

COPY jb-streamlit-ui/jugalbandi/streamlit-ui/ ./

EXPOSE 8080

CMD ["streamlit", "run", "--server.port", "8080", "Create_Knowledge_Base.py"]
