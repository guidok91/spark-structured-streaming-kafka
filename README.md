# Spark Structured Streaming Example
Spark Structured Streaming demo Python app.  
Consumes events from a Kafka topic, transforms and persists to a parquet file sink.

Structured Streaming is a scalable and fault-tolerant stream processing engine built on the Spark SQL engine.

## Running instructions
```shell script
spark-submit \
--master local[*] \
--conf spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 \
spark_structured_streaming_example/entrypoint.py
```
