POETRY_VERSION=1.8.5
DELTA_VERSION=$(shell poetry run python -c "from importlib.metadata import version; print(version('delta-spark'))")
SPARK_VERSION=$(shell poetry run python -c "from importlib.metadata import version; print(version('pyspark'))")
SPARK_ARGS = --master local[*] \
	--packages org.apache.spark:spark-sql-kafka-0-10_2.12:$(SPARK_VERSION),org.apache.spark:spark-avro_2.12:$(SPARK_VERSION),io.delta:delta-spark_2.12:$(DELTA_VERSION) \
	--conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
	--conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog

.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: setup
setup: # Set up virtual env with the app and its dependencies.
	pip install --upgrade pip setuptools wheel poetry==$(POETRY_VERSION)
	poetry config virtualenvs.in-project true --local
	poetry install

.PHONY: lint
lint: # Run code linting tools.
	poetry run pre-commit run --all-files

.PHONY: clean
clean: # Clean auxiliary files.
	rm -rf *.egg-info spark-warehouse metastore_db derby.log checkpoint/* checkpoint/.[!.]* .mypy_cache .ruff_cache data-lake-dev
	find . | grep -E "__pycache__" | xargs rm -rf
	touch checkpoint/.gitkeep

.PHONY: kafka-up
kafka-up: # Spin up local Kafka instance with Docker.
	docker-compose up -d

.PHONY: kafka-down
kafka-down: # Tear down local Kafka instance.
	docker-compose down

.PHONY: kafka-create-topic
kafka-create-topic: # Create Kafka topic for local dev.
	docker exec broker \
	kafka-topics \
	--bootstrap-server broker:9092 \
	--create \
	--topic movie.ratings.v1

.PHONY: kafka-produce-test-events
kafka-produce-test-events: # Produce dummy test events locally.
	poetry run python movie_ratings_streaming/produce_test_events.py

.PHONY: kafka-read-test-events
kafka-read-test-events: # Read and display local test events.
	docker exec --interactive --tty schema-registry \
	kafka-avro-console-consumer \
	--topic movie.ratings.v1 \
	--bootstrap-server broker:29092 \
	--property schema.registry.url=http://localhost:8081 \
	--from-beginning

.PHONY:
pyspark: # Run local pyspark console.
	poetry run pyspark \
	$(SPARK_ARGS)

.PHONY:
streaming-app-run: # Run Spark Structured streaming app locally.
	poetry run spark-submit \
	$(SPARK_ARGS) \
	movie_ratings_streaming/entrypoint.py
