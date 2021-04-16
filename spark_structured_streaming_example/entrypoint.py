from pyspark.sql.session import SparkSession
import yaml
import os
import logging
from lassystream.lassy_stream import LassyStream

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'conf', 'config.yml')


def load_config() -> dict:
    return yaml.load(
        open(CONFIG_FILE_PATH, 'r').read(),
        Loader=yaml.FullLoader
    )


def get_spark_session(spark_conf: dict) -> SparkSession:
    spark_session = SparkSession\
        .builder\
        .master(spark_conf.get('master'))\
        .config('spark.jars.packages', spark_conf.get('kafka_jar'))\
        .appName(spark_conf.get('app_name'))\
        .getOrCreate()

    spark_session.sparkContext.setLogLevel(spark_conf.get('log_level'))

    return spark_session


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-2s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    conf = load_config()
    spark_session = get_spark_session(conf.get('spark'))

    LassyStream(conf, spark_session).run()
