SHELL = /bin/bash
SPARK_ARGS = --master local[*] \
	--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0,io.delta:delta-core_2.12:2.2.0 \
	--conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
	--conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog

setup:
	pip install --upgrade pip setuptools wheel poetry
	poetry config virtualenvs.in-project true --local
	poetry install

code-style:
	poetry run black . && \
	poetry run isort --profile black .

clean:
	rm -rf *.egg-info spark-warehouse metastore_db derby.log checkpoint/* checkpoint/.[!.]*
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
	--topic movies_ratings

kafka-produce-test-events:
	poetry run python movie_ratings_streaming/produce_test_events.py

kafka-read-test-events:
	docker exec --interactive --tty schema-registry \
	kafka-avro-console-consumer \
	--topic movies_ratings \
	--bootstrap-server broker:9092 \
	--property schema.registry.url=http://localhost:8081 \
	--from-beginning

pyspark:
	poetry run pyspark \
	$(SPARK_ARGS)

streaming-app-run:
	poetry run spark-submit \
	$(SPARK_ARGS) \
	movie_ratings_streaming/entrypoint.py

vacuum:
	poetry run spark-sql \
	$(SPARK_ARGS) \
	-e "VACUUM movie_ratings RETAIN 168 HOURS"

compact-small-files:
	poetry run spark-sql \
	$(SPARK_ARGS) \
	-e "OPTIMIZE movie_ratings"
