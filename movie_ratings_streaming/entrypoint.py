import os
from configparser import ConfigParser

from pyspark.sql.session import SparkSession

from movie_ratings_streaming.stream import MovieRatingsStream

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")
SOURCE_AVRO_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "movie-ratings-avro-schema.json")


def _read_config() -> dict:
    config_parser = ConfigParser()
    config_parser.read(CONFIG_FILE_PATH)
    return dict(config_parser)


def _read_source_avro_schema() -> str:
    with open(SOURCE_AVRO_SCHEMA_PATH) as f:
        return f.read()


if __name__ == "__main__":
    config = _read_config()
    source_avro_schema = _read_source_avro_schema()

    spark_session = SparkSession.builder.getOrCreate()

    MovieRatingsStream(config, source_avro_schema, spark_session).run()
