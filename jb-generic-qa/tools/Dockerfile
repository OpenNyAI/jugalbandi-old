
FROM python:3.11.4-bullseye 

RUN apt-get -y update \ 
    && apt-get install -y ffmpeg \
    && wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.04.tar.gz \
    && tar -xvf xpdf-tools-linux-4.04.tar.gz && cp xpdf-tools-linux-4.04/bin64/pdftotext /usr/local/bin

RUN pip install --upgrade pip \
    && pip install --upgrade poetry \
    && python3 -m poetry config virtualenvs.in-project true

WORKDIR /app

COPY ./packages ./packages/
COPY ./jb-auth-service ./jb-auth-service/

WORKDIR /app/jb-generic-qa

COPY jb-generic-qa/pyproject.toml jb-generic-qa/poetry.lock jb-generic-qa/README.md ./
COPY jb-generic-qa/generic_qa/__init__.py ./generic_qa/

RUN python3 -m poetry install --only main

COPY jb-generic-qa/ ./

CMD tools/run-server.sh
