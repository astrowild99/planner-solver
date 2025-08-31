# Planner Solver

This project uses [Google OR-TOOLS](https://developers.google.com/optimization) to handle the planning for shop floor planning

## Local development

In order to start a local dev instance simply create a local venv

```shell
pyton3 -m venv .venv
pip install -r requirements.txt
```

Then start the docker by:
- copying .env.example to .env
- running the build in dev mode `docker compose up --build --watch`