setup :
	docker compose up -d
	cd frontend && npm i

be.start :
	docker compose up -d
be.stop :
	docker compose down

fe.dev :
	cd frontend && npm run dev

fake-ingest :
	curl -X POST http://localhost:5000/ingest-fake \
	  -H 'Content-Type: application/json' \
	  -d '{"date":"2025/11/28","count":200}'

# Dynamic spark-process with default values
# Usage: make spark-process YEAR=2025 MONTH=12 DAY=06 USER=john
YEAR ?= 2025
MONTH ?= 11
DAY ?= 28
USER ?= ash

spark-report :
	docker exec \
		-e S3_YEAR=$(YEAR) \
		-e S3_MONTH=$(MONTH) \
		-e S3_DAY=$(DAY) \
		-e TARGET_USERNAME=$(USER) \
		spark-master python3 /app/pysparkminioi.py
