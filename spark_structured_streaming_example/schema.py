from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


SOURCE_SCHEMA_LASSY = StructType([
    StructField('body', StructType([
        StructField('box_id', StringType()),
        StructField('carrier', StringType()),
        StructField('country', StringType()),
        StructField('customer_id', LongType()),
        StructField('datetime', StringType()),
        StructField('delivery_date', StringType()),
        StructField('est_delivery_time', StringType()),
        StructField('external_id', StringType()),
        StructField('hf_status', StringType()),
        StructField('location', StructType([
            StructField('city', StringType()),
            StructField('country', StringType()),
            StructField('state', StringType()),
            StructField('zip', StringType())
        ])),
        StructField('message', StringType()),
        StructField('public_url', StringType()),
        StructField('source', StringType()),
        StructField('status', StringType()),
        StructField('status_detail', StringType()),
        StructField('subscription_id', LongType()),
        StructField('tracking_code', StringType()),
        StructField('tracking_id', StringType()),
        StructField('type', StringType()),
        StructField('weight', DoubleType()),
    ])),
    StructField('header', StructType([
        StructField('Message - Type', StringType()),
        StructField('content - encoding', StringType()),
        StructField('content - type', StringType()),
        StructField('delivery - mode', StringType()),
        StructField('exchange', StringType()),
        StructField('routing - key', StringType()),
        StructField('timestamp', StringType()),
    ]))
])
