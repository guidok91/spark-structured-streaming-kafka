from pyspark.sql.session import SparkSession
from configparser import ConfigParser
import os
from spark_structured_streaming_demo.movie_ratings_stream import MovieRatingsStream


CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")


def _read_config() -> dict:
    config_parser = ConfigParser()
    config_parser.read(CONFIG_FILE_PATH)
    return dict(config_parser)


if __name__ == "__main__":
    config = _read_config()

    spark_session = SparkSession\
        .builder\
        .getOrCreate()

    MovieRatingsStream(config, spark_session).run()
