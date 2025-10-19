from dbm import sqlite3
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Customize the response for validation errors
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )

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

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: uuid.UUID):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (str(task_id),)
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Task not found")

        d = dict(row)
        d["status"] = Status(d["status"])
        return Task(**d)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: uuid.UUID):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (str(task_id),))

        if not cur.rowcount:
            raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: uuid.UUID, payload: TaskInput):
    with get_conn() as conn:
        exists = conn.execute(
            "SELECT 1 FROM tasks WHERE id = ?", (str(task_id),)
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Task not found")

        now = now_utc_iso()
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (payload.title, payload.description, payload.status.value, now, str(task_id)),
        )

        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (str(task_id),)
        ).fetchone()

        d = dict(row)
        d["status"] = Status(d["status"])
        return Task(**d)
    