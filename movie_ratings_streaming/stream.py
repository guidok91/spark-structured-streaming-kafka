import logging

from pyspark.sql.avro.functions import from_avro
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col
from pyspark.sql.session import SparkSession


class MovieRatingsStream:
    def __init__(self, config: dict, source_avro_schema: str, spark_session: SparkSession) -> None:
        self._config = config
        self._source_avro_schema = source_avro_schema
        self._spark_session = spark_session

    def run(self) -> None:
        df_input = self._read_stream()
        df_transformed = self._transform(df_input)
        self._write_stream(df_transformed)

    def _read_stream(self) -> DataFrame:
        topic = self._config["stream"]["source_kafka_topic"]

        stream = self._spark_session.readStream.format("kafka").option(
            "subscribe", topic
        )

        for k, v in self._config["kafka"].items():
            stream = stream.option(k, v)

        logging.info(f"Reading stream from topic {topic}...")
        df_raw = stream.load()

        return self._extract_payload(df_raw)

    def _extract_payload(self, df: DataFrame) -> DataFrame:
        return (
            df.select(
                from_avro(
                    data="value",
                    jsonFormatSchema=self._source_avro_schema
                ).alias("val")
            )
            .select("val.*")
        )

    @staticmethod
    def _transform(df: DataFrame) -> DataFrame:
        logging.info("Applying transformation...")
        final_fields = ["user_id", "movie_id", "rating", "rating_timestamp", "is_approved"]
        return df.withColumn("is_approved", col("rating") >= 7).select(final_fields)

    def _write_stream(self, df: DataFrame) -> None:
        logging.info("Writing stream...")

        sink_dir = self._config["stream"]["sink_dir"]
        checkpoint_dir = self._config["stream"]["checkpoint_dir"]
        trigger_processing_time = self._config["stream"]["trigger_processing_time"]
        output_mode = self._config["stream"]["output_mode"]

        (
            df.writeStream.format("parquet")
            .option("path", sink_dir)
            .option("checkpointLocation", checkpoint_dir)
            .outputMode(output_mode)
            .trigger(processingTime=trigger_processing_time)
            .start()
            .awaitTermination()
        )
