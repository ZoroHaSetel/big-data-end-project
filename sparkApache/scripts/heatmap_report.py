# file: heatmap_report.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, min as spark_min, max as spark_max
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime


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

    # 4. Filter for relevant events (include mouse move for better heatmap visualization)
    df_filtered = df.filter(
        col("action").isin(["mouse move", "mouse click", "mouse idle"])
    )

    # Check if we have data
    total_events = df_filtered.count()
    if total_events == 0:
        print("Warning: No events found matching filter criteria")
        spark.stop()
        return

    # Get overall statistics
    date_str = f"{year}/{month}/{day}"

    # Get unique users count if available
    unique_users_total = 0
    if "username" in df_filtered.columns:
        unique_users_total = df_filtered.select("username").distinct().count()

    # Get time range if available
    time_range_str = ""
    if "timestamp" in df_filtered.columns:
        time_range = df_filtered.agg(
            spark_min("timestamp").alias("min_ts"),
            spark_max("timestamp").alias("max_ts"),
        ).collect()[0]
        if time_range.min_ts and time_range.max_ts:
            min_time = datetime.fromtimestamp(time_range.min_ts / 1000)
            max_time = datetime.fromtimestamp(time_range.max_ts / 1000)
            time_range_str = (
                f"{min_time.strftime('%H:%M:%S')} - {max_time.strftime('%H:%M:%S')}"
            )

    # 5. Get list of unique pages
    pages = [row.page for row in df_filtered.select("page").distinct().collect()]

    # Create output directory
    output_dir = "/app/reports"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n=== Overall Statistics ===")
    print(f"Date: {date_str}")
    print(f"Total events: {total_events}")
    print(f"Unique users: {unique_users_total}")
    if time_range_str:
        print(f"Time range: {time_range_str}")
    print(f"Found pages: {pages}\n")

    # 6. Generate heatmap for each page
    for page in pages:
        print(f"Processing page: {page}")

        # Filter data for the specific page - include additional columns for statistics
        columns_to_select = ["x", "y", "action"]
        if "username" in df_filtered.columns:
            columns_to_select.append("username")
        if "timestamp" in df_filtered.columns:
            columns_to_select.append("timestamp")

        page_df = (
            df_filtered.filter(col("page") == page)
            .select(*columns_to_select)
            .toPandas()
        )

        if page_df.empty:
            print(f"No data for page {page}, skipping.")
            continue

        # Calculate statistics for this page
        total_page_events = len(page_df)

        # Event breakdown
        event_breakdown = {}
        if "action" in page_df.columns:
            action_counts = page_df["action"].value_counts()
            event_breakdown = {
                "mouse move": int(action_counts.get("mouse move", 0)),
                "mouse click": int(action_counts.get("mouse click", 0)),
                "mouse idle": int(action_counts.get("mouse idle", 0)),
            }

        # Unique users
        unique_users_page = 0
        avg_events_per_user = 0
        if "username" in page_df.columns:
            unique_users_page = page_df["username"].nunique()
            if unique_users_page > 0:
                avg_events_per_user = total_page_events / unique_users_page

        # Time range for this page
        page_time_range = ""
        if "timestamp" in page_df.columns:
            min_ts = page_df["timestamp"].min()
            max_ts = page_df["timestamp"].max()
            if pd.notna(min_ts) and pd.notna(max_ts):
                min_time = datetime.fromtimestamp(min_ts / 1000)
                max_time = datetime.fromtimestamp(max_ts / 1000)
                duration_seconds = (max_ts - min_ts) / 1000
                page_time_range = f"{min_time.strftime('%H:%M:%S')} - {max_time.strftime('%H:%M:%S')} ({duration_seconds/60:.1f} min)"

        # Coordinate statistics
        page_df_clean = page_df.dropna(subset=["x", "y"])
        if page_df_clean.empty:
            print(f"No valid coordinate data for page {page}, skipping.")
            continue

        x_min, x_max = page_df_clean["x"].min(), page_df_clean["x"].max()
        y_min, y_max = page_df_clean["y"].min(), page_df_clean["y"].max()

        # Calculate center points for reference lines
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2

        # Create the plot with larger figure to accommodate title and stats
        fig, ax = plt.subplots(figsize=(14, 10))

        # Filter out potential None values
        page_df_plot = page_df_clean.copy()

        # Create visualization
        kde_created = False
        scatter_plot = None

        if len(page_df_plot) < 2:
            print(f"Not enough data points for density plot on page {page}")
            # Fallback to scatter plot
            scatter_plot = sns.scatterplot(
                data=page_df_plot, x="x", y="y", hue="action", ax=ax, s=20, alpha=0.6
            )
        else:
            try:
                # KDE plot for density
                sns.kdeplot(
                    data=page_df_plot,
                    x="x",
                    y="y",
                    fill=True,
                    cmap="viridis",
                    alpha=0.7,
                    ax=ax,
                    levels=20,
                )
                # Scatter overlay
                scatter_plot = sns.scatterplot(
                    data=page_df_plot,
                    x="x",
                    y="y",
                    hue="action",
                    s=10,
                    alpha=0.5,
                    ax=ax,
                    edgecolors="white",
                    linewidth=0.3,
                )
                kde_created = True
            except Exception as e:
                print(f"KDE plot failed for {page}: {e}. Falling back to scatter.")
                scatter_plot = sns.scatterplot(
                    data=page_df_plot,
                    x="x",
                    y="y",
                    hue="action",
                    ax=ax,
                    s=20,
                    alpha=0.6,
                )

        # Add grid and reference lines
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
        ax.set_axisbelow(True)  # Grid behind plot elements

        # Add center reference lines
        ax.axvline(
            x=x_center,
            color="gray",
            linestyle=":",
            alpha=0.5,
            linewidth=1,
            label="Center X",
        )
        ax.axhline(
            y=y_center,
            color="gray",
            linestyle=":",
            alpha=0.5,
            linewidth=1,
            label="Center Y",
        )

        # Add quarter lines (optional - helps identify quadrants)
        if (
            x_max - x_min > 100 and y_max - y_min > 100
        ):  # Only if viewport is large enough
            x_quarter = (x_min + x_center) / 2
            x_three_quarter = (x_center + x_max) / 2
            y_quarter = (y_min + y_center) / 2
            y_three_quarter = (y_center + y_max) / 2
            ax.axvline(
                x=x_quarter, color="lightgray", linestyle=":", alpha=0.3, linewidth=0.5
            )
            ax.axvline(
                x=x_three_quarter,
                color="lightgray",
                linestyle=":",
                alpha=0.3,
                linewidth=0.5,
            )
            ax.axhline(
                y=y_quarter, color="lightgray", linestyle=":", alpha=0.3, linewidth=0.5
            )
            ax.axhline(
                y=y_three_quarter,
                color="lightgray",
                linestyle=":",
                alpha=0.3,
                linewidth=0.5,
            )

        # Comprehensive title block
        title_lines = [
            f"User Activity Heatmap - Page: {page}",
            f"Date: {date_str} | Events: {total_page_events} | Users: {unique_users_page}",
        ]
        if page_time_range:
            title_lines.append(f"Time: {page_time_range}")

        title_text = "\n".join(title_lines)
        ax.set_title(title_text, fontsize=12, fontweight="bold", pad=20)

        # Axis labels
        ax.set_xlabel("X Coordinate (pixels)", fontsize=10)
        ax.set_ylabel("Y Coordinate (pixels)", fontsize=10)
        ax.invert_yaxis()  # Web coordinates: (0,0) is top-left

        # Add legends
        # Colorbar for KDE density (if KDE plot was created)
        if kde_created and len(ax.collections) > 0:
            try:
                # Get the colorbar from the KDE plot collections on the axes
                cbar = plt.colorbar(ax.collections[0], ax=ax, pad=0.02)
                cbar.set_label(
                    "Activity Density", rotation=270, labelpad=15, fontsize=9
                )
            except Exception:
                # If colorbar creation fails, continue without it
                pass

        # Legend for action types (from scatter plot)
        if scatter_plot is not None:
            legend = ax.legend(
                title="Action Type", loc="upper right", framealpha=0.9, fontsize=9
            )
            legend.get_title().set_fontsize(9)

        # Statistics panel (text box in upper left)
        stats_lines = [
            "Statistics:",
            f"Total Events: {total_page_events}",
        ]

        if event_breakdown:
            stats_lines.append("")
            stats_lines.append("Event Breakdown:")
            for action, count in event_breakdown.items():
                if count > 0:
                    percentage = (count / total_page_events) * 100
                    stats_lines.append(f"  {action}: {count} ({percentage:.1f}%)")

        if unique_users_page > 0:
            stats_lines.append("")
            stats_lines.append(f"Unique Users: {unique_users_page}")
            stats_lines.append(f"Avg Events/User: {avg_events_per_user:.1f}")

        stats_lines.append("")
        stats_lines.append("Coordinate Range:")
        stats_lines.append(f"  X: {x_min:.0f} - {x_max:.0f}")
        stats_lines.append(f"  Y: {y_min:.0f} - {y_max:.0f}")

        stats_text = "\n".join(stats_lines)

        # Add statistics text box
        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="wheat", alpha=0.8),
            family="monospace",
        )

        # Add report generation timestamp in bottom right
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ax.text(
            0.98,
            0.02,
            f"Generated: {report_time}",
            transform=ax.transAxes,
            fontsize=7,
            horizontalalignment="right",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.7),
        )

        # Sanitize filename
        safe_page_name = page.replace("/", "_").strip("_")
        if not safe_page_name:
            safe_page_name = "root"

        filename = f"{output_dir}/heatmap_{safe_page_name}.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  ✓ Saved enhanced report to {filename}")
        print(
            f"    Events: {total_page_events} | Users: {unique_users_page} | Range: {x_min:.0f}-{x_max:.0f} x {y_min:.0f}-{y_max:.0f}"
        )

    spark.stop()
    print(f"\n=== Heatmap generation completed ===")
    print(f"Generated {len(pages)} enhanced heatmap(s) in {output_dir}")


if __name__ == "__main__":
    main()
