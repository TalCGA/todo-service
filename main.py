from dbm import sqlite3
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from db import init_db, get_conn
from schemas import Status, TaskInput, Task
from datetime import datetime, timezone
import uuid

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will run once at initialization
    init_db()
    yield

app = FastAPI(title="ToDo Service" , lifespan=lifespan)

@app.get("/tasks", response_model=list[Task])
def list_tasks():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()

        tasks: list[Task] = []
        for row in rows:
            d = dict(row)
            d["status"] = Status(d["status"]) 
            tasks.append(Task(**d))

        return tasks 

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_input: TaskInput):
    task_id = uuid.uuid4()
    now = now_utc_iso()

    try:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO tasks (id, title, description, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (str(task_id), task_input.title, task_input.description, task_input.status.value, now, now),
            )

            return Task(
                id=str(task_id),
                created_at=now,
                updated_at=now,
                **task_input.model_dump()
            )
    except sqlite3.Error as e:
        print(f"[DB ERROR] create_task failed: {e}")
        raise HTTPException(status_code=500, detail="Database error")
