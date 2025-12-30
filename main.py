from fastapi import FastAPI
from routes import auth, questions, assess

app = FastAPI()

app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(assess.router)