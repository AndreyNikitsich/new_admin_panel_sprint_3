FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates openssl tzdata make git \
    gcc g++ openssh-client \
    llvm zip unzip wget \
    libxml2-dev libxml2-utils liblz4-dev libxslt-dev build-essential libpq-dev \
    libgeoip-dev libjpeg-dev liblzma-dev libncurses5-dev libncursesw5-dev \
    libffi-dev libssl-dev dnsutils liblzma-dev postgresql-client \
    libunwind-dev procps curl vis vim grep bash gettext \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.7.1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /opt/app

RUN groupadd -r web && useradd -d /opt/app -r -g web web_user \
    && chown web_user:web -R /opt/app

COPY poetry.lock pyproject.toml ./
RUN poetry install $(test "$ENVIRONMENT" == production && echo "--no-dev") --no-interaction --no-ansi

COPY . .

EXPOSE 8000

USER web_user
ENTRYPOINT ["sh", "entrypoint.sh"]