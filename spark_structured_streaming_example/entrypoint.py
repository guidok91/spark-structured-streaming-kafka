from pyspark.sql.session import SparkSession
import yaml
import os
from spark_structured_streaming_example.movie_stream import MovieStream


CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'conf', 'config.yml')


if __name__ == '__main__':
    conf = yaml.load(
        open(CONFIG_FILE_PATH, 'r').read(),
        Loader=yaml.FullLoader
    )

    spark_session = SparkSession\
        .builder\
        .getOrCreate()

    MovieStream(conf, spark_session).run()
