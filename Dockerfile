FROM python:3.8-slim-buster

ENV POETRY_VERSION=1.1.1

RUN apt-get update \
    #&& apt-get install -y wget \
    && pip install poetry==$POETRY_VERSION \
    && mkdir solidumcapital


COPY ./pyproject.toml pyproject.toml
COPY ./poetry.lock poetry.lock
COPY ./solidumcapital/__init__.py solidumcapital/__init__.py
RUN poetry config virtualenvs.create false \
    && poetry install
RUN poetry run start