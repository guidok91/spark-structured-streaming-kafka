import datetime

from delta.tables import DeltaTable
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col, from_unixtime, lit, to_date
from pyspark.sql.session import SparkSession

LATE_ARRIVING_EVENTS_THRESHOLD_DAYS = 5


class MovieRatingsStream:
    """Reads streaming data from a Kafka topic, applies transformation and saves to a Delta sink."""

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
            "rating_timestamp",
            "rating_date",
        ]
        max_late_arriving_events_date = datetime.datetime.now(datetime.UTC).date() - datetime.timedelta(
            days=LATE_ARRIVING_EVENTS_THRESHOLD_DAYS
        )
        return (
            df.dropDuplicates(["event_id"])
            .withColumn("is_approved", col("rating") >= 7)
            .withColumn("rating_date", to_date(from_unixtime("rating_timestamp")))
            .where(col("rating_date") >= lit(max_late_arriving_events_date))
            .select(final_fields)
        )

    def _write_stream(self, df: DataFrame) -> None:
        checkpoint_path = self._config["stream"]["checkpoint_path"]
        output_mode = self._config["stream"]["output_mode"]

        (
            df.writeStream.format("delta")
            .foreachBatch(self._upsert_to_sink)
            .outputMode(output_mode)
            .option("checkpointLocation", checkpoint_path)
            .start()
            .awaitTermination()
        )

    def _upsert_to_sink(self, df: DataFrame, batch_id: int) -> None:
        output_path = self._config["stream"]["output_path"]
        self._create_sink_table_if_not_exists(output_path, df)
        sink_table = DeltaTable.forPath(self._spark_session, output_path)

        (
            sink_table.alias("existing")
            .merge(
                source=df.alias("incoming"),
                condition=f"""existing.event_id = incoming.event_id
                AND existing.rating_date >= DATE_ADD(CURRENT_DATE(), -{LATE_ARRIVING_EVENTS_THRESHOLD_DAYS})""",
            )
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )

    def _create_sink_table_if_not_exists(self, output_path: str, df: DataFrame) -> None:
        if not DeltaTable.isDeltaTable(self._spark_session, output_path):
            df.limit(0).write.format("delta").partitionBy(["rating_date"]).save(output_path)
