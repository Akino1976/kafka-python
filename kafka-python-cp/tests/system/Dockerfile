FROM test
ARG MOCK_AWS_HOST \
    DEFAULT_TIMEZONE \
    JOB_CONSUMER_SQS \
    S3_EXPORT_BUCKET \
    S3_AP_IMPORT_BUCKET \
    S3_IMPORT_BUCKET \
    AWS_PROFILE \
    AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY

ENV PYTHONPATH=$PYTHONPATH:/usr/src/tests/shared/:/usr/src/jobs/:/usr/src/tests/system/
WORKDIR /usr/src/tests/system
COPY . /usr/src/tests/system/

ENTRYPOINT ["py.test", "-c", "pytest.cfg"]
