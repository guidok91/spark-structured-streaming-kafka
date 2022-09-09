from setuptools import setup, find_packages


setup(
    name="spark_structured_streaming_demo",
    version="0.1",
    install_requires=["pyspark==3.3.0"],
    packages=find_packages(),
    description="Spark Structured Streaming demo app",
    author="Guido Kosloff Gancedo"
)
