FROM bitnami/spark as spark_base

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=$PYTHONPATH:/app/src \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.6.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

USER root
RUN apt-get update && apt-get install -y \
    curl \
    bash \
    libffi-dev \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

FROM spark_base as builder

RUN apt-get update && apt-get install -y  \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR $PYSETUP_PATH

RUN curl -sSL https://install.python-poetry.org | python3 -
COPY poetry.lock* pyproject.toml ./

ARG DEBUG=false
RUN poetry install $(test ! $DEBUG && echo "--no-dev")

FROM spark_base as final

RUN curl https://jdbc.postgresql.org/download/postgresql-42.2.18.jar -o /opt/bitnami/spark/jars/postgresql-42.2.18.jar

COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH
COPY .. /app


WORKDIR /app

ENTRYPOINT ["docker/app/entrypoint.sh"]

