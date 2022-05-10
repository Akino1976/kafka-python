# Kafka in confluent-python
Want to test workflow for kafka before deploying? This repo give that opportunity to mock a dataset with version controlled schema-registry in order to test how the data will look at destination.

## some codes
For installing confluent-kafka locally and using brew.
```
pip install --global-option=build_ext --global-option="-I/usr/local/Cellar/librdkafka/1.8.2/include" --global-option="-L/usr/local/Cellar/librdkafka/1.8.2//lib" confluent-kafka
```
Check if a file is in S3 with localstack:
```
aws --endpoint-url=http://localhost:4566 s3 ls s3://eu-docker-data-eu --recursive
```
Want to breakpoint in a python script?
```
breakpoint()
```
and enter save inside **test_all.py** when in watch-mode to rerun the test.
