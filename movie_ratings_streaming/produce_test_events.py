import logging
import socket
import time
import uuid
from random import uniform

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from movie_ratings_streaming.config.config import read_config, read_source_avro_schema


def acked(err, msg):  # type: ignore
    if err is not None:
        logging.error(f"Failed to deliver message: {msg.value()}: {err}")
    else:
        logging.info(f"Message produced: {msg.value()}")


if __name__ == "__main__":
    """Ad-hoc script to produce continuous Avro events to the local Kafka broker."""
    logging.basicConfig(level=logging.INFO)

    config = read_config()
    source_avro_schema = read_source_avro_schema()
    topic = config["kafka"]["subscribe"]

    avro_serializer = AvroSerializer(
        schema_registry_client=SchemaRegistryClient({"url": config["kafka"]["schema.registry.url"]}),
        schema_str=source_avro_schema,
    )
    producer = SerializingProducer(
        {
            "bootstrap.servers": config["kafka"]["kafka.bootstrap.servers"],
            "client.id": socket.gethostname(),
            "value.serializer": avro_serializer,
        }
    )

    while True:
        producer.produce(
            topic=topic,
            value={
                "event_id": str(uuid.uuid1()),
                "user_id": str(uuid.uuid1()),
                "movie_id": str(uuid.uuid1()),
                "rating": round(uniform(0, 10), 1),
                "rating_timestamp": int(time.time()),
            },
            on_delivery=acked,
        )
        producer.poll()
