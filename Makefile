SHELL=/bin/bash

setup:
	python -m venv .venv && \
	source .venv/bin/activate && \
	pip install --upgrade pip wheel setuptools && \
	pip install -e .

clean:
	rm -rf *.egg-info data_lake/checkpoint/.[!.]* data_lake/sink/.[!.]*
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
	kafka-topics --bootstrap-server broker:9092 \
	--create --topic movies.ratings

kafka-produce-test-events:
	docker exec --interactive --tty broker \
	kafka-console-producer --bootstrap-server broker:9092 \
	--topic movies.ratings

kafka-read-test-events:
	docker exec --interactive --tty broker \
	kafka-console-consumer --bootstrap-server broker:9092 \
	--topic movies.ratings \
	--from-beginning

streaming-app-run:
	source .venv/bin/activate && \
	spark-submit \
	--master local[*] \
	--conf spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 \
	spark_structured_streaming_demo/entrypoint.py
