ARG PYTHON_VERSION=3.10.1
FROM python:${PYTHON_VERSION}
ARG SCHEMA_REGISTRY_LISTENERS \
    MOCK_AWS_HOST \
    ENVIRONMENT \
    JOB_CONSUMER_SQS \
    S3_IMPORT_BUCKET \
    S3_EXPORT_BUCKET

ENV POETRY_VERSION=1.1.13 \
    KAFKA_VERSION=1.6.2 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN curl -L --compressed https://github.com/edenhill/librdkafka/archive/v${KAFKA_VERSION}.tar.gz -o v${KAFKA_VERSION}.tar.gz \
    && tar xvzf v${KAFKA_VERSION}.tar.gz \
    && cd librdkafka-${KAFKA_VERSION}/ \
    && ./configure \
    && make \
    && make install \
    && ldconfig \
    && rm -rf v${KAFKA_VERSION}.tar.gz

RUN apt-get update && apt-get install -y librdkafka-dev
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv"

WORKDIR /usr/src/tests/
COPY poetry.lock pyproject.toml /usr/src/tests/

RUN poetry install
ENTRYPOINT [ "/bin/sh" ]
