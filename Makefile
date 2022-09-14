SHELL=/bin/bash

setup:
	pip install --upgrade pip setuptools wheel poetry
	poetry config virtualenvs.in-project true --local
	poetry install

code-style:
	poetry run black . && \
	poetry run isort --profile black .

clean:
	rm -rf *.egg-info data_lake/checkpoint/* data_lake/checkpoint/.[!.]* data_lake/sink/* data_lake/sink/.[!.]*
	touch data_lake/checkpoint/.gitkeep
	touch data_lake/sink/.gitkeep

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

streaming-app-run:
	poetry run spark-submit \
	--master local[*] \
	--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0 \
	movie_ratings_streaming/entrypoint.py
