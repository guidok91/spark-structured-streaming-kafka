from pyspark.sql.avro.functions import from_avro
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col, from_unixtime, to_date
from pyspark.sql.session import SparkSession


class MovieRatingsStream:
    """Reads streaming data from a Kafka topic, applies transformation and saves to a Parquet file sink."""

    def __init__(
        self, config: dict, source_avro_schema: str, spark_session: SparkSession
    ) -> None:
        self._config = config
        self._source_avro_schema = source_avro_schema
        self._spark_session = spark_session

    def run(self) -> None:
        df_input = self._read_stream()
        df_transformed = self._transform(df_input)
        self._write_stream(df_transformed)

    def _read_stream(self) -> DataFrame:
        stream = self._spark_session.readStream.format("kafka")

        for k, v in self._config["kafka"].items():
            stream = stream.option(k, v)

        df_raw = stream.load()

        return self._extract_payload(df_raw)

    def _extract_payload(self, df: DataFrame) -> DataFrame:
        """Deserializes topic `value` from Avro.
        First 5 bytes need to be skipped since they are reserved for Confluent's internal Wire format:
        https://docs.confluent.io/platform/current/schema-registry/serdes-develop/index.html#wire-format
        """
        return (
            df.selectExpr("SUBSTRING(value, 6) AS avro_value")
            .select(
                from_avro(
                    data=col("avro_value"),
                    jsonFormatSchema=self._source_avro_schema,
                ).alias("val")
            )
            .select("val.*")
        )

    @staticmethod
    def _transform(df: DataFrame) -> DataFrame:
        final_fields = [
            "user_id",
            "movie_id",
            "rating",
            "rating_timestamp",
            "is_approved",
            "rating_date",
        ]
        return (
            df.withColumn("is_approved", col("rating") >= 7)
            .withColumn("rating_date", to_date(from_unixtime("rating_timestamp")))
            .select(final_fields)
        )

    def _write_stream(self, df: DataFrame) -> None:
        sink_table = self._config["stream"]["sink_table"]
        checkpoint_dir = self._config["stream"]["checkpoint_dir"]
        trigger_processing_time = self._config["stream"]["trigger_processing_time"]
        output_mode = self._config["stream"]["output_mode"]

        (
            df.writeStream.format("delta")
            .partitionBy(["rating_date"])
            .outputMode(output_mode)
            .trigger(processingTime=trigger_processing_time)
            .option("checkpointLocation", checkpoint_dir)
            .toTable(sink_table)
            .awaitTermination()
        )
