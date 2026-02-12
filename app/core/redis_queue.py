<<<<<<< HEAD
<<<<<<< HEAD
import redis, json, os
=======
=======
>>>>>>> 38aa2aa (Implement scanner webhook response and update schemas; configure Docker and docker-compose for backend service)
import os
import redis
import json

<<<<<<< HEAD
>>>>>>> d8493e6 (dockerfile and docker-compose setup)
=======
=======
import redis, json, os
>>>>>>> d9b4b4e (Implement scanner webhook response and update schemas; configure Docker and docker-compose for backend service)
>>>>>>> 38aa2aa (Implement scanner webhook response and update schemas; configure Docker and docker-compose for backend service)

class RedisClient:
    addr = os.getenv("REDIS_ADDR", "redis:6379")

    def __init__(
<<<<<<< HEAD
<<<<<<< HEAD
        self, 
        host: str = addr.split(":")[0],
        port: int = addr.split(":")[1],
=======
        self,
        host: str | None = None,
        port: int | None = None,
>>>>>>> d8493e6 (dockerfile and docker-compose setup)
=======
        self,
        host: str | None = None,
        port: int | None = None,
=======
        self, 
        host: str = addr.split(":")[0],
        port: int = addr.split(":")[1],
>>>>>>> d9b4b4e (Implement scanner webhook response and update schemas; configure Docker and docker-compose for backend service)
>>>>>>> 38aa2aa (Implement scanner webhook response and update schemas; configure Docker and docker-compose for backend service)
        db: int = 0,
        decode_responses: bool = True,
    ):
        host = host or os.getenv("REDIS_HOST", "localhost")
        port = port if port is not None else int(os.getenv("REDIS_PORT", "6379"))
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)


    def PushToQueue(self, queue_name: str = "scan_queue", data: dict = {}):
        self.redis.lpush(queue_name, json.dumps(data))

    def PopFromQueue(self, queue_name: str = "scan_queue"):
        return self.redis.brpop(queue_name)  