from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "ShieldStat"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

def get_user_collection():
    return db["users"]

def get_questions_collection():
    return db["questions"]

def get_assessment_results_collection():
    return db["assessmentresults"]