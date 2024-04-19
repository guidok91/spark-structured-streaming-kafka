import os
from configparser import ConfigParser

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.ini")
SOURCE_AVRO_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "movie-ratings-avro-schema.avsc")


def read_config() -> dict:
    config_parser = ConfigParser()
    config_parser.read(CONFIG_FILE_PATH)
    return dict(config_parser)


def read_source_avro_schema() -> str:
    with open(SOURCE_AVRO_SCHEMA_PATH) as f:
        return f.read()
