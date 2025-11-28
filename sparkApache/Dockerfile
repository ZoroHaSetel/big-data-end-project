FROM spark:3.5.3-scala2.12-java17-ubuntu

# Install Python and dependencies as root
USER root
RUN set -ex; \
    apt-get update; \
    apt-get install -y python3 python3-pip; \
    rm -rf /var/lib/apt/lists/*

# Create /app and explicitly chown it to the spark user (UID 185)
RUN mkdir -p /app && \
    chown spark:spark /app

# Copy requirements and install Python packages
COPY requirements.txt /app/requirements.txt
COPY scripts/pysparkminioi.py /app/pysparkminioi.py
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Remove any conflicting legacy AWS bundles if present
RUN rm -f /opt/spark/jars/aws-java-sdk-bundle-*.jar

# Download hadoop-aws integration (compatible with Spark 3.5 / Hadoop 3.3.x)
RUN wget -q -O /opt/spark/jars/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar

# Download AWS SDK v1 bundle (compatible with hadoop-aws 3.3.4)
RUN wget -q -O /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar



# Optional: create a directory where the spark user will write code/results
RUN mkdir /app/code && chown spark:spark /app/code

EXPOSE 8080 7077

# Switch to non-root spark user
USER spark

CMD ["/app/pysparkminioi.py"]
