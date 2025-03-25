# Spark Structured Streaming Demo
[Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) data pipeline that processes movie ratings data in real-time.

Consumes events from a Kafka topic in Avro, transforms and writes to a [Delta](https://delta.io/) table.

The pipeline handles updates and duplicate events by merging to the destination table based on the `event_id`.

Late arriving events from more than 5 days ago are discarded (for performance reasons in the merge - to leverage partitioning and avoid full scans).

## Data Architecture
![data architecture](https://github.com/user-attachments/assets/adea51b9-f5f3-41a6-b623-98982453fd31)

## Local setup
We spin up a local Kafka cluster with Schema Registry based on the [Docker Compose file provided by Confluent](https://github.com/confluentinc/cp-all-in-one/blob/7.8.0-post/cp-all-in-one-community/docker-compose.yml).

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
>>> df = spark.read.format("delta").load(path="data-lake-dev/movie_ratings")
>>> df.show()
+--------------------+--------------------+------+-----------+----------------+-----------+
|             user_id|            movie_id|rating|is_approved|rating_timestamp|rating_date|
+--------------------+--------------------+------+-----------+----------------+-----------+
|0c67b5fe-8cf7-11e...|0c67b6b2-8cf7-11e...|   1.8|      false|      1672933621| 2023-01-05|
|601f90a8-8cf8-11e...|601f9152-8cf8-11e...|   9.5|       true|      1672934191| 2023-01-05|
|6249323a-8cf8-11e...|624932da-8cf8-11e...|   3.1|      false|      1672934194| 2023-01-05|
+--------------------+--------------------+------+-----------+----------------+-----------+
```

## Table internal maintenance
The streaming microbatches produce lots of small files in the target table. This is not optimal for subsequent reads.

In order to tackle this issue, the following properties are enabled on the Spark session:
- Auto compaction: to periodically merge small files into bigger ones automatically.
- Optimized writes: to write bigger sized files automatically.

More information can be found on [the Delta docs](https://docs.delta.io/latest/optimizations-oss.html).
