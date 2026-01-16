# Spark Structured Streaming Demo
[Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) data pipeline that processes movie ratings data in real-time.

Consumes events from a Kafka topic in Avro, transforms and writes to an [Apache Iceberg](https://iceberg.apache.org/) table.

The pipeline handles updates and duplicate events by merging to the destination table based on the `event_id`.
The output table is partitioned by `days(rating_timestamp)` (leveraging [Iceberg's hidden partitioning](https://iceberg.apache.org/docs/latest/partitioning/) for optimal querying)

## Data Architecture
<img width="1731" alt="image" src="https://github.com/user-attachments/assets/79551b02-e192-4203-9d6b-2ce07253056f" />

## Local setup
We spin up a local Kafka cluster with Schema Registry based on the [Docker Compose file provided by Confluent](https://github.com/confluentinc/cp-all-in-one/blob/v8.1.1/cp-all-in-one-community/docker-compose.yml).

We install a local Spark Structured Streaming app using uv.

## Dependency management
Dependabot is configured to periodically upgrade repo dependencies. See [dependabot.yml](.github/dependabot.yml).

## Running instructions
Run the following commands in order:
* `make setup` to install the Spark Structured Streaming app on a local Python env.
* `make kafka-up` to start local Kafka in Docker.
* `make kafka-create-topic` to create the Kafka topic we will use.
* `make kafka-produce-test-events` to start writing messages to the topic.

On a separate console, run:
* `make streaming-app-run` to start the Spark Structured Streaming app.

On a separate console, you can check the output dataset by running:
```python
$ make pyspark
>>> df = spark.read.table("movie_ratings")
>>> df.show()
+--------------------+--------------------+--------------------+------+-----------+----------------+-----------+
|            event_id|             user_id|            movie_id|rating|is_approved|rating_timestamp|rating_date|
+--------------------+--------------------+--------------------+------+-----------+----------------+-----------+
|a41847d0-37de-11f...|a418482a-37de-11f...|a418483e-37de-11f...|   1.8|      false|      1748008982| 2025-05-23|
|a46519c0-37de-11f...|a4651a42-37de-11f...|a4651a60-37de-11f...|   6.9|      false|      1748008982| 2025-05-23|
|a4c15a50-37de-11f...|a4c15ac8-37de-11f...|a4c15ae6-37de-11f...|   5.0|      false|      1748008983| 2025-05-23|
|a79b2b98-37de-11f...|a79b2c10-37de-11f...|a79b2c2e-37de-11f...|   4.0|      false|      1748008988| 2025-05-23|
+--------------------+--------------------+--------------------+------+-----------+----------------+-----------+
```

## Table internal maintenance
The streaming microbatches can produce many small files and constant table snapshots.

In order to tackle these issues, the recommended Iceberg table maintenance operations can be used, [see doc](https://iceberg.apache.org/docs/latest/spark-structured-streaming/#maintenance-for-streaming-tables).
