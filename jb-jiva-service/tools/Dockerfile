
FROM python:3.11.4-bullseye 

RUN pip install --upgrade pip \
    && pip install --upgrade poetry \
    && python3 -m poetry config virtualenvs.in-project true

WORKDIR /app

COPY ./packages ./packages/
COPY ./jb-auth-service ./jb-auth-service/

WORKDIR /app/jb-jiva-service

COPY jb-jiva-service/pyproject.toml jb-jiva-service/poetry.lock jb-jiva-service/README.md ./
COPY jb-jiva-service/jiva/__init__.py ./jiva/

RUN python3 -m poetry install --only main

COPY jb-jiva-service/ ./

CMD tools/run-server.sh
