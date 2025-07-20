FROM python:3.11-alpine AS python_upstream

RUN apk add bash

FROM python_upstream AS dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml pyproject.toml

COPY src src
COPY configs configs

RUN pip install .

CMD "planner-solver"