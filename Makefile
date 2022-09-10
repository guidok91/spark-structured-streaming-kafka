SHELL=/bin/bash

setup:
	python -m venv .venv && \
	source .venv/bin/activate && \
	pip install --upgrade pip wheel setuptools && \
	pip install -e .

clean:
	rm -rf *.egg-info data_lake/checkpoint/* data_lake/checkpoint/.[!.]* data_lake/sink/* data_lake/sink/.[!.]*
	touch data_lake/checkpoint/.gitkeep
	touch data_lake/sink/.gitkeep

kafka-start:
	docker-compose up -d

kafka-stop:
	docker-compose stop

kafka-rm:
	docker-compose rm -f

kafka-create-topic:
	docker exec broker \
	kafka-topics \
	--bootstrap-server broker:9092 \
	--create \
	--topic movies.ratings

kafka-produce-test-events:
	docker exec --interactive --tty schema-registry \
	kafka-avro-console-producer \
	--topic movies.ratings \
	--bootstrap-server broker:9092 \
	--property schema.registry.url=http://localhost:8081 \
	--property value.schema="$$(< movie_ratings_streaming/movie-ratings-avro-schema.json)"

kafka-read-test-events:
	docker exec --interactive --tty schema-registry \
	kafka-avro-console-consumer \
	--topic movies.ratings \
	--bootstrap-server broker:9092 \
	--property schema.registry.url=http://localhost:8081 \
	--from-beginning

streaming-app-run:
	source .venv/bin/activate && \
	spark-submit \
	--master local[*] \
	--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0 \
	movie_ratings_streaming/entrypoint.py
