Project for mouse tracking using big data

Goal :

Generate attention heatmap from mouse tracking data , using big data processing

Solution :

- We'll first implement a website with mouse tracking functionality
    - We'll use docker to host the website
- We'll use library to stream the mouse tracking data to big data processing system
- We'll store this data under minio 
- We'll use spark to process this data and generate attention heatmap
- We'll map the heatmap to the website and display it to report back to user



Frontend :
- Simple pokemon landing page
- Mouse tracking functionality using simple script collect mouse position every 1s and and send it to backend every 30s
- docker for frontend hosting

Backend :
- basic rest api using fastapi
- Use to collect mouse tracking data from frontend
- API include
    - track : collect mouse tracking data from frontend , store it in minio
    - healthcheck : check if backend is running

Big data stack:

- utilise pyspark read data from minio and process it


Libraries :
- docker for frontend hosting
- minio for big data processing
- spark for big data processing
- mouse tracking library

Task :

- Create a landing page for the website
- Implement mouse tracking functionality
- Implement big data processing system
- Implement minio storage system
- Implement spark processing system
- Implement heatmap generation system
- Implement heatmap mapping system
- Implement heatmap display system



Prepartion 
curl -X POST http://localhost:5000/ingest-fake  -H 'Content-Type: application/json'  -d '{"date":"2025/11/28","count":200}'

docker exec spark-master python3 /app/pysparkminioi.py