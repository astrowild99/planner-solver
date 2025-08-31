FROM python:3.12.3-slim AS python_upstream

# RUN apk add bash

FROM python_upstream AS dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chmod=755 docker/entrypoint-dev.sh "entrypoint.sh"
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
RUN mkdir /etc/secrets

COPY pyproject.toml pyproject.toml

COPY src src
COPY configs base_configs

RUN pip install -e .

CMD "planner-solver"

FROM dev AS test

CMD echo "Ready" && sleep infinity