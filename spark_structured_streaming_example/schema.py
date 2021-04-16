from pyspark.sql.types import StructType, StructField, LongType, StringType, ArrayType


SOURCE_SCHEMA_MOVIES = StructType([
        StructField('cast', ArrayType(StringType())),
        StructField('genres', ArrayType(StringType())),
        StructField('title', StringType()),
        StructField('year', LongType())
    ])
