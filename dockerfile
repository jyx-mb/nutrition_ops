#/start from an image that already has python 3.13
FROM python:3.13-slim

#/ /app as working folder inside container
WORKDIR /app

#/ install uv
RUN pip install uv

#/ copy just the 2 deps first, so docker can reuse this layer when only code changes later
COPY pyproject.toml uv.lock ./

#/ install deps in a venv inside
## --frozen = obey the lockfile exactly, --no-intall-project = deps only, --no-dev = skip test tool

RUN uv sync --frozen --no-install-project --no-dev
#/ copy api code into the image
COPY app.py ./

## copy mlflow db (records where the model lives)
COPY mlflow.db ./

## copy the model files themselves (whole mlruns folder)
COPY mlruns ./mlruns

## put venv's programs on PATH for calling fastapi directly
ENV PATH="/app/.venv/bin:$PATH"

## tell docker the app listens on port 8000
EXPOSE 8000

## start the api in production mode on 0.0.0.0 to be reachable from outside of container
CMD ["fastapi", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
