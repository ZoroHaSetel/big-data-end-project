# file: simple_pyspark_test.py
# python testspark1.py
# spark-submit --master local testspark1.py

from pyspark.sql import SparkSession

# Create Spark session in local mode
spark = SparkSession.builder.appName("SimpleTest").master("local[*]").getOrCreate()

# Quick test: create a small DataFrame and perform an action
data = [("Alice", 34), ("Bob", 45), ("Catherine", 29)]
columns = ["name", "age"]

df = spark.createDataFrame(data, columns)

print("PySpark is working!")
df.show()

# Stop the session
spark.stop()
