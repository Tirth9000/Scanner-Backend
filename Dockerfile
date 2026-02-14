<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
FROM python:3.14.2

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD [ "python", "main.py" ]
=======
=======
>>>>>>> 38aa2aa (Implement scanner webhook response and update schemas; configure Docker and docker-compose for backend service)
=======
>>>>>>> d8493e6 (dockerfile and docker-compose setup)
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["python", "app/main.py"]
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> d8493e6 (dockerfile and docker-compose setup)
=======
=======
FROM python:3.14.2

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD [ "python", "main.py" ]
>>>>>>> d9b4b4e (Implement scanner webhook response and update schemas; configure Docker and docker-compose for backend service)
>>>>>>> 38aa2aa (Implement scanner webhook response and update schemas; configure Docker and docker-compose for backend service)
=======
>>>>>>> d8493e6 (dockerfile and docker-compose setup)
