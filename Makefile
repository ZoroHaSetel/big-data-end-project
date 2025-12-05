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
spark-process :
	docker exec spark-master python3 /app/pysparkminioi.py