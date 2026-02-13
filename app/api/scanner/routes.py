from fastapi import APIRouter
from api.scanner.service import create_scan_task_to_queue
from api.scanner.schemas import RequestScanTask
from core.redis_queue import RedisClient
import json
from db.base import getCursor


router = APIRouter(prefix='/api/scanner', tags=["scanner"])

@router.post("/register-scan-task")
async def register_scan_task(request: RequestScanTask):
    result = await create_scan_task_to_queue(request)
    scan_id = result["scan_id"]

    cursor = getCursor()
    cursor.execute(
        """
        INSERT INTO scan_results(user_id, scan_id, domain, results)
        VALUES (%s, %s, %s, %s)
        """,
        (
            request.user_id,
            scan_id,
            request.target,
            json.dumps({'status': 'pending'})
        ),
    )
    cursor.close()
    return result


@router.get("/scanlist")
def get_scan_list():
    redis_client = RedisClient() 
    data = redis_client.redis.lrange("scan_queue", 0, -1)
    return  [json.loads(item) for item in data]
    # return [item for item in data]

@router.get("/clear")
def clear_scan_queue():
    redis_client = RedisClient() 
    redis_client.redis.delete("scan_queue")
    return {"message": "Scan queue cleared"}