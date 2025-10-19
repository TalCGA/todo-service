from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import init_db


app = FastAPI(title="ToDo Service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will run once at initialization
    init_db()
    yield

@app.get("/")
def root():
    return {"message": "backend check"}
