
FROM python:3.11.4-bullseye 


RUN pip install --upgrade pip \
    && pip install --upgrade poetry \
    && python3 -m poetry config virtualenvs.in-project true

WORKDIR /app
COPY ./packages ./packages/
COPY ./jb-auth-service ./jb-auth-service/

WORKDIR /app/jb-labeling-service

COPY jb-labeling-service/pyproject.toml jb-labeling-service/poetry.lock jb-labeling-service/README.md ./
COPY jb-labeling-service/labeling/__init__.py ./labeling/

RUN python3 -m poetry install --only main

COPY jb-labeling-service/ ./

CMD tools/run-server.sh
