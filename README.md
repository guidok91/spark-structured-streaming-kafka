# Spark Structured Streaming Demo
[Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) demo app (PySpark).

Consumes events in real-time from a Kafka topic in Avro, transforms and persists to an [Iceberg](https://iceberg.apache.org/) table.

## Local setup
We spin up a local Kafka cluster with Schema Registry using a [Docker Compose file provided by Confluent](https://developer.confluent.io/tutorials/kafka-console-consumer-producer-avro/kafka.html#get-confluent-platform).

## Running instructions
Run the following commands in order:
* `make setup` to install the Spark Structured Streaming app on a local Python env.
* `make kafka-up` to start local Kafka in Docker.
* `make kafka-create-topic` to create the Kafka topic we will use.
* `make kafka-produce-test-events` to start writing messages to the topic.

On a separate console, run:
* `make create-output-table` to create the output Iceberg table.
* `make streaming-app-run` to start the Spark Structured Streaming app.

You can check the output dataset by running:
```python
$ make pyspark
>>> df = spark.read.table("iceberg.default.movie_ratings")
>>> df.show()                                                                   
+--------------------+--------------------+------+----------------+-----------+
|             user_id|            movie_id|rating|rating_timestamp|is_approved|
+--------------------+--------------------+------+----------------+-----------+
|f3c413bf-ab29-4e9...|30f90f95-b90a-452...|   8.9|   1642236375000|       true|
|7c70a6de-5352-41c...|fcade620-b844-41c...|   7.6|   1642239975000|       true|
|08da4c50-7bf6-4f1...|6441219e-18f0-452...|   6.8|   1642209780000|      false|
+--------------------+--------------------+------+----------------+-----------+
```
