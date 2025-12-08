from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import io
import os
from minio import Minio
from minio.error import S3Error
from datetime import datetime, timedelta
import random


app = Flask(__name__)
# Enable CORS - allow all origins for development
CORS(app)

client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key="admin",
    secret_key="password123",
    secure=False,
)

bucket_name = "mouse-data"

if not client.bucket_exists(bucket_name=bucket_name):
    client.make_bucket(bucket_name=bucket_name)


@app.post("/collect")
def collect():
    data = request.get_json()
    today = datetime.now().strftime("%Y/%m/%d")
    object_name = f"raw/{today}/events_{int(datetime.now().timestamp()*1000)}.json"

    json_bytes = json.dumps(data).encode("utf-8")
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=io.BytesIO(json_bytes),
        length=len(json_bytes),
    )
    return "ok", 200


# curl -X POST http://localhost:5000/ingest-fake \
#   -H 'Content-Type: application/json' \
#   -d '{"date":"2025/11/28","count":200}'


@app.post("/ingest-fake")
def ingest_fake():
    """Generate fake mouse events and upload them to Minio under `raw/<date>/`.

    Request JSON (optional):
      - date: string in 'YYYY/MM/DD' format (default: '2025/11/28')
      - count: integer number of events to generate (default: 100)

    Returns JSON: {"status": "ok", "object": <object_name>, "count": <n>}
    """
    req = request.get_json(silent=True) or {}
    date_str = req.get("date", "2025/11/28")
    try:
        dt = datetime.strptime(date_str, "%Y/%m/%d")
    except Exception:
        return jsonify({"error": "invalid date format, expected YYYY/MM/DD"}), 400

    count = int(req.get("count", 100))

    start_ts = int(dt.replace(hour=0, minute=0, second=0).timestamp())
    end_ts = start_ts + 86400 - 1

    actions = ["mouse click", "mouse idle", "mousemove"]
    pages = ["/", "/login", "/selection", "/confirm"]
    user = ["ash", "unknown", "guest", "admin"]

    events = []
    for i in range(count):
        ev = {
            "username": f"user{random.randint(1,20)}",
            "action": random.choice(actions),
            "page": random.choice(pages),
            "timestamp": random.randint(start_ts * 1000, end_ts * 1000),
            "x": random.randint(0, 1920),
            "y": random.randint(0, 1080),
            "username": random.choice(user),
        }
        events.append(ev)

    object_name = (
        f"raw/{date_str}/events_fake_{int(datetime.now().timestamp()*1000)}.json"
    )
    try:
        json_bytes = json.dumps(events).encode("utf-8")
        client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=io.BytesIO(json_bytes),
            length=len(json_bytes),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok", "object": object_name, "count": len(events)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
