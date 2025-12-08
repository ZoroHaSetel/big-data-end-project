# file: pyspark_read_from_minio.py
# docker exec spark-master python3 /app/pysparkminioi.py
# file: pyspark_read_from_minio.py
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def main():
    # 1. Create SparkSession with MinIO/S3A configuration
    spark = (
        SparkSession.builder.appName("MinIO-MouseData-FilterUser")
        .master("local[*]")
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
        .config("spark.hadoop.fs.s3a.access.key", "admin")
        .config("spark.hadoop.fs.s3a.secret.key", "password123")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config(
            "spark.sql.files.maxPartitionBytes", "134217728"
        )  # 128 MB per partition
        .getOrCreate()
    )

    # 2. Define the S3A path (adjust date/folder as needed)
    # Read from environment variables, with sensible defaults
    bucket = os.getenv("S3_BUCKET", "mouse-data")
    year = os.getenv("S3_YEAR", "2025")
    month = os.getenv("S3_MONTH", "11")
    day = os.getenv("S3_DAY", "28")

    s3_path = f"s3a://{bucket}/raw/{year}/{month}/{day}/*.json"
    print(f"Reading from S3A path: {s3_path}")

    # 3. Read JSON data from MinIO
    df = spark.read.option("multiline", "true").json(s3_path)

    # 4. Display schema for verification
    print("=== Schema ===")
    df.printSchema()

    # 5. Filter events for the specific user
    target_username = os.getenv("TARGET_USERNAME", "ash")

    df_filtered = df.filter(col("username") == target_username)

    # Optional: select only relevant columns for cleaner output
    df_selected = df_filtered.select(
        "username", "action", "page", "timestamp", "x", "y"
    ).orderBy("timestamp")

    # 6. Show results
    print(f"\n=== Mouse events for user: {target_username} ===")
    df_selected.show(50, truncate=False)

    # 7. (Optional) Get count of events for this user
    count = df_selected.count()
    print(f"Total events recorded for user '{target_username}': {count}")

    # 8. Clean up
    spark.stop()
    print("\nSpark session stopped. Processing completed.")


if __name__ == "__main__":
    main()
