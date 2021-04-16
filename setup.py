from setuptools import setup, find_packages

NAME = 'spark_structured_streaming_example'
VERSION = '0.1'

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name=NAME,
    version=VERSION,
    install_requies=REQUIREMENTS,
    package_data={'spark_structured_streaming_example': ['*.yml', '*.p12', '*.jks']},
    packages=find_packages(),
    description='Spark Structured Streaming demo Python app',
    author='Guido Kosloff Gancedo'
)
