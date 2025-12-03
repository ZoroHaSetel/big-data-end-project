setup :
	docker compose up -d
	cd frontend && npm i

run :
	docker compose up -d
stop :
	docker compose down

frontend :
	cd frontend && npm start
