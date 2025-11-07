UV_VERSION=0.9.7
ICEBERG_VERSION=1.10.0
SPARK_VERSION=$(shell uv run python -c "from importlib.metadata import version; print(version('pyspark'))")
SPARK_ARGS = --master local[*] \
	--packages org.apache.spark:spark-sql-kafka-0-10_2.13:$(SPARK_VERSION),org.apache.spark:spark-avro_2.13:$(SPARK_VERSION),org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:$(ICEBERG_VERSION) \
	--conf spark.sql.defaultCatalog=local \
	--conf spark.sql.catalog.local=org.apache.iceberg.spark.SparkCatalog \
	--conf spark.sql.catalog.local.type=hadoop \
	--conf spark.sql.catalog.local.warehouse=data-lake-dev

.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: setup
setup: # Set up virtual env with the app and its dependencies.
	curl -LsSf https://astral.sh/uv/$(UV_VERSION)/install.sh | sh
	uv sync

.PHONY: lint
lint: # Run code linting tools.
	uv run pre-commit run --all-files

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
	uv run python movie_ratings_streaming/produce_test_events.py

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
	uv run pyspark \
	$(SPARK_ARGS)

.PHONY:
streaming-app-run: # Run Spark Structured streaming app locally.
	uv run spark-submit \
	$(SPARK_ARGS) \
	movie_ratings_streaming/entrypoint.py
