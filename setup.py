from setuptools import setup, find_packages


setup(
    name="movie_ratings_streaming",
    version="0.1",
    install_requires=["pyspark==3.3.0"],
    packages=find_packages(),
    description="Spark Structured Streaming + Kafka demo app",
    author="Guido Kosloff Gancedo"
)
