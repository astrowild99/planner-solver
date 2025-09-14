FROM python:3.12.3-slim AS python_upstream

# RUN apk add bash

FROM python_upstream AS dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN sed -i '/^-e /d' requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY vendor vendor
RUN pip install -e vendor/bunnet

COPY --chmod=755 docker/entrypoint-dev.sh "entrypoint.sh"
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
RUN mkdir /etc/secrets

COPY pyproject.toml pyproject.toml

COPY src src
COPY configs base_configs

RUN pip install -e .

CMD "planner-solver"

FROM dev AS test

ENV PYTHONBUFFERED=1

COPY --chmod=755 docker/entrypoint-test.sh "/usr/src/app/entrypoint.sh"
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

COPY tests tests

CMD echo "Ready" && sleep infinity