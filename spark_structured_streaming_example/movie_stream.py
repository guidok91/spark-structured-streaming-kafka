import logging
from pyspark.sql.session import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import from_json, col, explode
from spark_structured_streaming_example.schema import SOURCE_SCHEMA_MOVIES


class MovieStream:

    def __init__(self, conf: dict, spark_session: SparkSession):
        self._conf = conf
        self._spark_session = spark_session

    def run(self) -> None:
        df_input = self._read_stream()
        df_transformed = self._transform(df_input)
        self._write_stream(df_transformed)

    def _read_stream(self) -> DataFrame:
        topic = self._conf.get('stream').get('source_kafka_topic')

        stream = self._spark_session\
            .readStream\
            .format('kafka')\
            .option('subscribe', topic)

        for k, v in self._conf.get('kafka').items():
            stream = stream.option(k, v)

        logging.info(f'Reading stream from topic {topic}...')
        df_raw = stream.load()

        return self._extract_payload(df_raw)

    @staticmethod
    def _extract_payload(df: DataFrame) -> DataFrame:
        return df\
            .selectExpr('CAST(value AS STRING)')\
            .select(from_json(col('value'), SOURCE_SCHEMA_MOVIES).alias('val'))\
            .select('val.*')

    @staticmethod
    def _transform(df: DataFrame) -> DataFrame:
        logging.info('Applying transformation...')
        return df.select(
            'cast',
            'title',
            explode('genres').alias('genre'),
            'year'
        )

    def _write_stream(self, df: DataFrame) -> None:
        logging.info('Writing stream...')

        sink_dir = self._conf.get('stream').get('sink_dir')
        checkpoint_dir = self._conf.get('stream').get('checkpoint_dir')
        trigger_processing_time = self._conf.get('stream').get('trigger_processing_time')
        output_mode = self._conf.get('stream').get('output_mode')
        nr_partitions_per_batch = self._conf.get('stream').get('nr_partitions_per_batch')

        query = df\
            .coalesce(nr_partitions_per_batch)\
            .writeStream\
            .format('parquet')\
            .option('path', sink_dir)\
            .option('checkpointLocation', checkpoint_dir)\
            .outputMode(output_mode)\
            .trigger(processingTime=trigger_processing_time)\
            .start()

        query.awaitTermination()
