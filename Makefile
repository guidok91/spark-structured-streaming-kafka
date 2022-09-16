SHELL=/bin/bash
SPARK_ARGS=--master local[*] \
	--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0,org.apache.iceberg:iceberg-spark-runtime-3.2_2.12:0.14.0 \
	--conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
	--conf spark.sql.catalog.iceberg=org.apache.iceberg.spark.SparkCatalog \
	--conf spark.sql.catalog.iceberg.type=hadoop \
	--conf spark.sql.catalog.iceberg.warehouse=spark-warehouse

setup:
	pip install --upgrade pip setuptools wheel poetry
	poetry config virtualenvs.in-project true --local
	poetry install

code-style:
	poetry run black . && \
	poetry run isort --profile black .

clean:
	rm -rf *.egg-info spark-warehouse checkpoint/* checkpoint/.[!.]*
	touch checkpoint/.gitkeep

kafka-up:
	docker-compose up -d

kafka-down:
	docker-compose down

kafka-create-topic:
	docker exec broker \
	kafka-topics \
	--bootstrap-server broker:9092 \
	--create \
	--topic movies.ratings

kafka-produce-test-events:
	poetry run python movie_ratings_streaming/produce_test_events.py

kafka-read-test-events:
	docker exec --interactive --tty schema-registry \
	kafka-avro-console-consumer \
	--topic movies.ratings \
	--bootstrap-server broker:9092 \
	--property schema.registry.url=http://localhost:8081 \
	--from-beginning

create-output-table:
	poetry run spark-sql \
	$(SPARK_ARGS) \
	-e "CREATE TABLE IF NOT EXISTS iceberg.default.movie_ratings (user_id STRING, movie_id STRING, rating FLOAT, rating_timestamp BIGINT, is_approved BOOLEAN) USING iceberg"

pyspark:
	poetry run pyspark \
	$(SPARK_ARGS)

streaming-app-run:
	poetry run spark-submit \
	$(SPARK_ARGS) \
	movie_ratings_streaming/entrypoint.py
