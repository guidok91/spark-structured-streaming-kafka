# Spark Structured Streaming Demo
Spark Structured Streaming demo app (PySpark).

Consumes events from a Kafka topic, transforms and persists to a parquet file sink.

Structured Streaming is a scalable and fault-tolerant stream processing engine built on the Spark SQL engine.

## Running instructions
Run the following commands in order:
* `make kafka-start` to start local Kafka in Docker.
* `make kafka-create-topic` to create the Kafka topic we will use.
* `make kafka-produce-test-events` to write some messages to the topic. You can write the following ones and then press `Ctrl-D` to exit:
    ```json
    {"user_id": "f3c413bf-ab29-4e9c-8233-2da4aaf04980", "movie_id": "30f90f95-b90a-452f-a934-162eb10437c7", "rating": 8.9, "rating_timestamp": 1642236375000}
    {"user_id": "7c70a6de-5352-41c6-886d-e3ef990e7f2b", "movie_id": "fcade620-b844-41cc-bc40-e244f334e6e0", "rating": 7.6, "rating_timestamp": 1642239975000}
    {"user_id": "08da4c50-7bf6-4f10-b621-d298c758ed03", "movie_id": "6441219e-18f0-452b-953d-d2278f47b68f", "rating": 6.8, "rating_timestamp": 1642209780000}
    ```
* `make setup` to create a local Python venv and install the Spark Structured Streaming app.
* `make streaming-app-run` to start the Spark Structured Streaming app.

Check the output dataset:

```python
$ python -m venv .venv
$ pyspark
>>> df = spark.read.parquet("data_lake/sink")
>>> df.show()                                                                   
+--------------------+--------------------+------+----------------+-----------+
|             user_id|            movie_id|rating|rating_timestamp|is_approved|
+--------------------+--------------------+------+----------------+-----------+
|f3c413bf-ab29-4e9...|30f90f95-b90a-452...|   8.9|   1642236375000|       true|
|7c70a6de-5352-41c...|fcade620-b844-41c...|   7.6|   1642239975000|       true|
|08da4c50-7bf6-4f1...|6441219e-18f0-452...|   6.8|   1642209780000|      false|
+--------------------+--------------------+------+----------------+-----------+
```


You can also open a separate console and produce more events to the topic.
