from dotenv import load_dotenv
load_dotenv()  # Load env vars FIRST before other imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.auth import router as authRouter
from app.db.sessions import init_db, init_tables

app = FastAPI()

# Initialize database on startup
init_db()
init_tables()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(authRouter)


@app.get('/')
def root():
    return "ShieldStat backend is running"