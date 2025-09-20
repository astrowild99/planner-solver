#!/bin/bash

set -e

docker compose -f compose.test.yaml up --build -d

docker compose -f compose.test.yaml exec planner-solver pytest tests -sv