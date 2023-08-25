# Spark Structured Streaming Demo
[Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) demo app (PySpark).

Consumes movie rating events in real-time from a Kafka topic in Avro, transforms and writes to a [Delta](https://delta.io/) table.

The pipeline handles updates and duplicate events by upserting to the destination table based on the `event_id`.

Late arriving events from more than 5 days ago are discarded (for performance reasons in the upsert).

## Data Architecture
![data architecture](https://user-images.githubusercontent.com/38698125/209481709-08c7a921-553a-4cd5-9327-055bcb23b1d5.png)

## Local setup
We spin up a local Kafka cluster with Schema Registry using a [Docker Compose file provided by Confluent](https://developer.confluent.io/tutorials/kafka-console-consumer-producer-avro/kafka.html#get-confluent-platform).

We install a local Spark Structured Streaming app using Poetry.

## Running instructions
Run the following commands in order:
* `make setup` to install the Spark Structured Streaming app on a local Python env.
* `make kafka-up` to start local Kafka in Docker.
* `make kafka-create-topic` to create the Kafka topic we will use.
* `make kafka-produce-test-events` to start writing messages to the topic.

On a separate console, run:
* `make create-sink-table` to create the destination Delta table.
* `make streaming-app-run` to start the Spark Structured Streaming app.

On a separate console, you can check the output dataset by running:
```python
$ make pyspark
>>> df = spark.read.table("movie_ratings")
>>> df.show()                                                                   
+--------------------+--------------------+------+-----------+----------------+-----------+
|             user_id|            movie_id|rating|is_approved|rating_timestamp|rating_date|
+--------------------+--------------------+------+-----------+----------------+-----------+
|0c67b5fe-8cf7-11e...|0c67b6b2-8cf7-11e...|   1.8|      false|      1672933621| 2023-01-05|
|601f90a8-8cf8-11e...|601f9152-8cf8-11e...|   9.5|       true|      1672934191| 2023-01-05|
|6249323a-8cf8-11e...|624932da-8cf8-11e...|   3.1|      false|      1672934194| 2023-01-05|
+--------------------+--------------------+------+-----------+----------------+-----------+
```

## Table maintenance
The streaming microbatches produce:
- Lots of small files in the table.
- Constant new Delta table versions.

Therefore, we can periodically run these two maintenance processes to mitigate the issues above:
- `make compact-small-files`
- `make vacuum`
