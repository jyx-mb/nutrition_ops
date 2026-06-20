# nutrition_ops

An educational MLOps project: a food recommendation pipeline built on open data
from the Swedish Food Agency (Livsmedelsverket).

The goal is not the smartest model, but a complete, honest pipeline:
data versioning, experiment tracking, API serving, containerization,
cloud deployment, CI/CD, and monitoring.

## Disclaimer

This is a learning project, NOT medical or nutritional advice. 
Health-profile rules are simplified derivations from published reference
values (Nordic Nutrition Recommendations 2023), for educational purposes only. 
Consult a qualified professional for real dietary decisions.

## Data

Source: Livsmedelsverkets Livsmedelsdatabas (Swedish Food Agency),
via their open API. Database version: pinned at data import.
Data is used unmodified, as the source requires.

## Status

 [x] Level 0 — repo, environment, git
 [ ] Level 1 — data + baseline model
 [ ] Level 2 — experiment tracking + data versioning
 [ ] Level 3 — API + Docker
 [ ] Level 4 — AWS + Terraform + CI/CD
 [ ] Level 5 — monitoring + drift detection