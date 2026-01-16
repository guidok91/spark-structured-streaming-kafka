from pyspark.sql import Catalog, DataFrame
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col, days
from pyspark.sql.session import SparkSession


class MovieRatingsStream:
    """Reads streaming data from a Kafka topic, applies transformation and saves to an Iceberg sink."""

    def __init__(self, config: dict, source_avro_schema: str, spark_session: SparkSession) -> None:
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
            "event_id",
            "user_id",
            "movie_id",
            "rating",
            "is_approved",
            "rating_timestamp"
        ]
        return (
            df.dropDuplicates(["event_id"])
            .withColumn("is_approved", col("rating") >= 7)
            .withColumn("rating_timestamp", col("rating_timestamp").cast("timestamp"))
            .select(final_fields)
        )

    def _write_stream(self, df: DataFrame) -> None:
        checkpoint_path = self._config["stream"]["checkpoint_path"]
        output_table = self._config["stream"]["output_table"]
        trigger_processing_time = self._config["stream"]["trigger_processing_time"]
        self._create_sink_table_if_not_exists(output_table, df)

        (
            df.writeStream.format("iceberg")
            .trigger(processingTime=trigger_processing_time)
            .option("fanout-enabled", "true")
            .option("checkpointLocation", checkpoint_path)
            .foreachBatch(self._upsert_to_sink)
            .start()
            .awaitTermination()
        )

    def _upsert_to_sink(self, df: DataFrame, batch_id: int) -> None:
        df.createOrReplaceGlobalTempView("incoming")
        self._spark_session.sql(f"""
            MERGE INTO {self._config["stream"]["output_table"]} existing
            USING (SELECT * FROM global_temp.incoming) as incoming
            ON existing.event_id = incoming.event_id
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """)

    def _create_sink_table_if_not_exists(self, output_table: str, df: DataFrame) -> None:
        if not Catalog(self._spark_session).tableExists(tableName=output_table):
            empty_batch_df = self._spark_session.createDataFrame([], df.schema)
            empty_batch_df.writeTo(output_table).using("iceberg").partitionedBy(days("rating_timestamp")).create()
