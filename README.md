# nutrition_ops

An educational MLOps project: a food-group classification pipeline built on open data
from the Swedish Food Agency (Livsmedelsverket).

The goal is not the smartest model, but a complete, honest pipeline:
data versioning, experiment tracking, API serving, containerization,
cloud deployment, CI/CD, and monitoring.

## Disclaimer

This is a learning project, NOT medical or nutritional advice.

## Data

Source: Livsmedelsverkets Livsmedelsdatabas (Swedish Food Agency),
via their open API. Database version: pinned at data import.
Data is a little lighter but  used unmodified, as the source requires.

## How To Run

#/Install the dependencies
```
uv sync
start the API (http://127.0.0.1:8000):
uv run fastapi dev app.py
run the tests:
uv run pytest -v
```
## Status

 [ ] → [x] Level 0 — repo, environment, git
 [ ] → [x] Level 1 — data + baseline model
 [ ] → [x] Level 2 — experiment tracking + data versioning
 [ ] → [x] Level 3 — API + Docker
 [ ] Level 4 — AWS + Terraform + CI/CD
 [ ] Level 5 — monitoring + drift detection
