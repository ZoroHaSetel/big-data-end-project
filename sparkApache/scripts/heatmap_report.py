# file: heatmap_report.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


def main():
    # 1. Create SparkSession with MinIO/S3A configuration
    spark = (
        SparkSession.builder.appName("MinIO-Heatmap-Report")
        .master("local[*]")
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
        .config("spark.hadoop.fs.s3a.access.key", "admin")
        .config("spark.hadoop.fs.s3a.secret.key", "password123")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.sql.files.maxPartitionBytes", "134217728")
        .getOrCreate()
    )

    # 2. Define the S3A path
    # Read from environment variables, with sensible defaults
    bucket = os.getenv("S3_BUCKET", "mouse-data")
    year = os.getenv("S3_YEAR", "2025")
    month = os.getenv("S3_MONTH", "11")
    day = os.getenv("S3_DAY", "28")
    
    s3_path = f"s3a://{bucket}/raw/{year}/{month}/{day}/*.json"

    # 3. Read JSON data
    try:
        df = spark.read.option("multiline", "true").json(s3_path)
    except Exception as e:
        print(f"Error reading data: {e}")
        spark.stop()
        return

    # 4. Filter for relevant events
    df_filtered = df.filter(col("action").isin("mousemove", "mouse click"))

    # 5. Get list of unique pages
    pages = [row.page for row in df_filtered.select("page").distinct().collect()]

    # Create output directory
    output_dir = "/app/reports"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Found pages: {pages}")

    # 6. Generate heatmap for each page
    for page in pages:
        print(f"Processing page: {page}")

        # Filter data for the specific page
        page_df = (
            df_filtered.filter(col("page") == page)
            .select("x", "y", "action")
            .toPandas()
        )

        if page_df.empty:
            print(f"No data for page {page}, skipping.")
            continue

        # Create the plot
        plt.figure(figsize=(12, 8))

        # Use kdeplot for density heatmap
        # Filter out potential None values just in case
        page_df = page_df.dropna(subset=["x", "y"])

        if len(page_df) < 2:
            print(f"Not enough data points for density plot on page {page}")
            # Fallback to scatter plot
            sns.scatterplot(data=page_df, x="x", y="y", hue="action")
        else:
            try:
                sns.kdeplot(
                    data=page_df, x="x", y="y", fill=True, cmap="viridis", alpha=0.7
                )
                sns.scatterplot(
                    data=page_df, x="x", y="y", hue="action", s=10, alpha=0.5
                )  # Overlay points
            except Exception as e:
                print(f"KDE plot failed for {page}: {e}. Falling back to scatter.")
                sns.scatterplot(data=page_df, x="x", y="y", hue="action")

        plt.title(f"User Activity Heatmap - Page: {page}")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.gca().invert_yaxis()  # Web coordinates: (0,0) is top-left

        # Sanitize filename
        safe_page_name = page.replace("/", "_").strip("_")
        if not safe_page_name:
            safe_page_name = "root"

        filename = f"{output_dir}/heatmap_{safe_page_name}.png"
        plt.savefig(filename)
        plt.close()
        print(f"Saved report to {filename}")

    spark.stop()
    print("Heatmap generation completed.")


if __name__ == "__main__":
    main()
