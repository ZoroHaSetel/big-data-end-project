from flask import Flask, request
from flask_cors import CORS
import json
import io
import os
from minio import Minio
from minio.error import S3Error
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key="admin",
    secret_key="password123",
    secure=False
)

bucket_name = "mouse-data"

if not client.bucket_exists(bucket_name=bucket_name):
    client.make_bucket(bucket_name=bucket_name)

@app.post('/collect')
def collect():
    data = request.get_json()
    today = datetime.now().strftime("%Y/%m/%d")
    object_name = f"raw/{today}/events_{int(datetime.now().timestamp()*1000)}.json"
    
    json_bytes = json.dumps(data).encode('utf-8')
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=io.BytesIO(json_bytes),
        length=len(json_bytes)
    )
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)