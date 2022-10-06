ARG PYTHON_VERSION=3.9


FROM python:${PYTHON_VERSION}-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    APP_PATH="/code" \
    VENV_PATH="/code/.venv" \
    USE_DOCKER=true \
    PYTHONPATH="$PYTHONPATH:/code/tests"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

WORKDIR $APP_PATH


# Build
FROM python-base as builder-base

ARG DJANGO_VERSION=3.1.7

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# get poetry
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get --no-install-recommends install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python -

ENV PATH="${PATH}:/root/.poetry/bin"


COPY pyproject.toml poetry.lock ./

# install deps
RUN poetry update django==${DJANGO_VERSION} && poetry install --no-root

# Prod
FROM python-base as production
COPY --from=builder-base $APP_PATH $APP_PATH
COPY . $APP_PATH
