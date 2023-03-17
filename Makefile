SPARK_ARGS = --master local[*] \
	--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.apache.spark:spark-avro_2.12:3.3.2,io.delta:delta-core_2.12:2.2.0 \
	--conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
	--conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog

.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: setup
setup: # Set up local virtual env for development.
	pip install --upgrade pip setuptools wheel poetry
	poetry config virtualenvs.in-project true --local
	poetry install

.PHONY: lint
lint: # Run code linter tools.
	poetry run black . && \
	poetry run isort --profile black .

.PHONY: clean
clean: # Clean auxiliary files.
	rm -rf *.egg-info spark-warehouse metastore_db derby.log checkpoint/* checkpoint/.[!.]*
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
	--topic movies_ratings

.PHONY: kafka-produce-test-events
kafka-produce-test-events: # Produce dummy test events locally.
	poetry run python movie_ratings_streaming/produce_test_events.py

.PHONY: kafka-read-test-events
kafka-read-test-events: # Read and display local test events.
	docker exec --interactive --tty schema-registry \
	kafka-avro-console-consumer \
	--topic movies_ratings \
	--bootstrap-server broker:9092 \
	--property schema.registry.url=http://localhost:8081 \
	--from-beginning

.PHONY: 
pyspark: # Run local pyspark console.
	poetry run pyspark \
	$(SPARK_ARGS)

.PHONY: 
spark-sql: # Run local spark sql console.
	poetry run spark-sql \
	$(SPARK_ARGS)

.PHONY: 
create-sink-table: # Create sink Delta table locally.
	poetry run spark-sql \
	$(SPARK_ARGS) \
	-e "CREATE TABLE movie_ratings ( \
		user_id STRING, \
		movie_id STRING, \
		rating FLOAT, \
		is_approved BOOLEAN, \
		rating_timestamp BIGINT \
	) \
	USING DELTA \
	PARTITIONED BY (rating_date DATE)"

.PHONY: 
streaming-app-run: # Run Spark Structured streaming app locally.
	poetry run spark-submit \
	$(SPARK_ARGS) \
	movie_ratings_streaming/entrypoint.py

.PHONY: 
vacuum: # Run Delta vacuum command on the sink table.
	poetry run spark-sql \
	$(SPARK_ARGS) \
	-e "VACUUM movie_ratings RETAIN 168 HOURS"

.PHONY: 
compact-small-files: # Run Delta optimize command on the sink table.
	poetry run spark-sql \
	$(SPARK_ARGS) \
	-e "OPTIMIZE movie_ratings"
