FROM python:3.12.9-alpine

# install poetry
RUN pip install poetry==2.1.1

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN touch README.md && \
    poetry install --only main --no-root --no-directory && \
    rm -rf $POETRY_CACHE_DIR

COPY src ./src
COPY start.sh ./

RUN poetry install --only main

#ENTRYPOINT ["poetry", "run", "./start.sh"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]

ENTRYPOINT gunicorn --bind :3000 --workers 1 --threads 2 --timeout 0 app:main 