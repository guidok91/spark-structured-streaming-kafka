from setuptools import find_packages, setup

setup(
    name="movie_ratings_streaming",
    version="0.1",
    install_requires=["pyspark==3.3.0", "black~=22.8.0", "isort~=5.10.1"],
    packages=find_packages(),
    description="Spark Structured Streaming + Kafka demo app",
    author="Guido Kosloff Gancedo",
)
