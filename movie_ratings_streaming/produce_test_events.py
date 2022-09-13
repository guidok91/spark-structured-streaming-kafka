import logging
import socket

from confluent_kafka import Producer

from movie_ratings_streaming.config.config import read_config


def acked(err, msg):
    if err is not None:
        logging.error(f"Failed to deliver message: {msg.value()}: {err}")
    else:
        logging.info(f"Message produced: {msg.value()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = read_config()
    producer_config = {
        "bootstrap.servers": config["kafka"]["kafka.bootstrap.servers"],
        "client.id": socket.gethostname(),
    }
    topic = config["stream"]["source_kafka_topic"]

    logging.info(
        f"Starting Kafka producer with the following config: {producer_config}"
    )
    producer = Producer(producer_config)

    # TODO produce random avro events in a loop
    logging.info(f"Producing to topic {topic}")
    producer.produce(topic=topic, value="hahahahaha", callback=acked)

    producer.poll(1)
