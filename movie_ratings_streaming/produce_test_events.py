import logging
import socket
import time
import uuid
from random import randint, uniform

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from movie_ratings_streaming.config.config import read_config, read_source_avro_schema


def acked(err, msg):
    if err is not None:
        logging.error(f"Failed to deliver message: {msg.value()}: {err}")
    else:
        logging.info(f"Message produced: {msg.value()}")


if __name__ == "__main__":
    """Ad-hoc script to produce continuous Avro events to the local Kafka broker."""
    logging.basicConfig(level=logging.INFO)

    config = read_config()
    source_avro_schema = read_source_avro_schema()
    topic = config["stream"]["source_kafka_topic"]

    schema_registry_config = {"url": config["kafka"]["schema.registry.url"]}
    schema_registry_client = SchemaRegistryClient(schema_registry_config)

    avro_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=source_avro_schema,
    )

    producer_config = {
        "bootstrap.servers": config["kafka"]["kafka.bootstrap.servers"],
        "client.id": socket.gethostname(),
        "value.serializer": avro_serializer,
    }
    producer = SerializingProducer(producer_config)

    while 1:
        producer.produce(
            topic=topic,
            value={
                "user_id": str(uuid.uuid1()),
                "movie_id": str(uuid.uuid1()),
                "rating": round(uniform(0, 10), 1),
                "rating_timestamp": randint(1609459200000, 1661990400000),
            },
            on_delivery=acked,
        )
        producer.poll(1)
        time.sleep(1)
