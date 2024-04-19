from pyspark.sql.session import SparkSession

from movie_ratings_streaming.config.config import read_config, read_source_avro_schema
from movie_ratings_streaming.stream import MovieRatingsStream

if __name__ == "__main__":
    config = read_config()
    source_avro_schema = read_source_avro_schema()

    spark_session = (
        SparkSession.builder.appName("Movie ratings streaming data pipeline")
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .config("spark.databricks.delta.autoCompact.enabled", "true")
        .config("spark.databricks.delta.optimizeWrite.enabled", "true")
        .enableHiveSupport()
        .getOrCreate()
    )

    MovieRatingsStream(config, source_avro_schema, spark_session).run()
