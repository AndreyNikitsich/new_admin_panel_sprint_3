FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates openssl tzdata make git \
    gcc g++ openssh-client \
    llvm zip unzip wget \
    libxml2-dev libxml2-utils liblz4-dev libxslt-dev build-essential libpq-dev \
    libgeoip-dev libjpeg-dev liblzma-dev libncurses5-dev libncursesw5-dev \
    libffi-dev libssl-dev dnsutils liblzma-dev postgresql-client \
    libunwind-dev procps curl vis vim grep bash gettext pipx\
    && rm -rf /var/lib/apt/lists/*

RUN pipx ensurepath && pipx install poetry

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE "false"

WORKDIR /opt/app

RUN groupadd -r web && useradd -d /opt/app -r -g web web_user \
    && chown web_user:web -R /opt/app

COPY poetry.lock poetry.lock
RUN poetry install --no-root

COPY . .