REPOSITORY := kafka-python
KAFKA_IMAGE := kafka
LOCAL_STACK=0.14.2
PROJECT_DIR := $(realpath $(CURDIR))
PYTHON_VERSION := 3.10.1
ENVIRONMENT ?= staging
CURRENT_DATE := $(shell echo `date +'%Y-%m-%d'`)
VERSION ?= commit_$(shell git rev-parse --short HEAD)
POETRY_FILE := poetry.lock pyproject.toml
AWS_IMAGE_ID := $(shell docker ps --filter ancestor=localstack/localstack:$(LOCAL_STACK) --format {{.ID}})

COMPOSE_DEFAULT_FLAGS := -f docker-compose.yaml
COMPOSE_TEST_FLAGS := $(COMPOSE_DEFAULT_FLAGS) -f docker-compose-test.yaml

export CURRENT_DATE
export REPOSITORY
export VERSION
export PROJECT_DIR
export ENVIRONMENT
export PYTHON_VERSION
export KAFKA_IMAGE
export LOCAL_STACK

###########################################################################
# Dependent containers
###########################################################################
echo_dir:
	@echo $(PROJECT_DIR)

create-network:
	@echo "=>  Creating network 'kafka_bridge'"
	@docker network create -d bridge kafka_bridge 2>/dev/null || true

###########################################################################
# Test containers enviroment, hack for keeping lock file in one place and
# utlize lock files during build in testing
###########################################################################
BUILD_DIR := $(PROJECT_DIR)
DESTINATION_DIRS := tests/shared
$(DESTINATION_DIRS)/%: $(BUILD_DIR)/%
	@echo "=> Moving $< to $@"
	@cp $< $@
copy-poetry: $(patsubst %, $(DESTINATION_DIRS)/%, $(POETRY_FILE))

.PHONY: set-up-environment
set-up-environment: copy-poetry build-kafka-image

.PHONY: kafka-environment
kafka-environment:
	docker-compose $(COMPOSE_TEST_FLAGS) up -d schema-registry

systemtests: set-up-environment
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm systemtests

systemtests-watch: set-up-environment
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm systemtests-watch

unittests: copy-poetry build-kafka-image
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm unittests

unittests-watch: copy-poetry
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm unittests-watch

tests: systemtests unittests
###########################################################################
# docker commands
###########################################################################
build-%:
	docker-compose $(COMPOSE_TEST_FLAGS) build $*

run-%:
	docker-compose $(COMPOSE_TEST_FLAGS) run $*

stop-all-containers:
	docker ps -q | xargs -I@ docker stop @

clear-all-containers: stop-all-containers
	docker ps -aq | xargs -I@ docker rm @

clear-volumes: clear-all-containers
	docker volume ls -q | xargs -I@ docker volume rm @

clear-images: clear-volumes
	docker images -q | uniq | xargs -I@ docker rmi -f @
