from dbm import sqlite3
from typing import Optional
from click import UUID
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
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
def list_tasks(
    status: Status | None = None,
    date_field_filter: str = "created_at",     
    since: str | None = None,          
    until: str | None = None,           
    sort: str = "created_at",          
    direction: str = "desc",    
    limit: int = 50,
    offset: int = 0,
):
    errors = []

    ALLOWED_DATE_FIELDS = {"created_at", "updated_at"}
    ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "status"}
    ALLOWED_DIRS = {"asc", "desc"}

    if date_field_filter not in ALLOWED_DATE_FIELDS:
        errors.append(f"Invalid date_field: {date_field_filter}")
    if sort not in ALLOWED_SORT_FIELDS:
        errors.append(f"Invalid sort field: {sort}")
    if direction not in ALLOWED_DIRS:
        errors.append(f"Invalid direction: {direction}")
    if not (1 <= limit <= 100):
        errors.append("limit must be between 1 and 100")
    if offset < 0:
        errors.append("offset must be >= 0")

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    if sort == "status":
        order_by = f"CASE status WHEN 'open' THEN 1 WHEN 'in_progress' THEN 2 WHEN 'done' THEN 3 END {direction.upper()}"
    else:
        order_by = f"{sort} {direction.upper()}"

    sql = f"""
    SELECT * FROM tasks
    WHERE (:status IS NULL OR status = :status)
      AND (:since  IS NULL OR substr({date_field_filter}, 1, 10) >= :since)
      AND (:until  IS NULL OR substr({date_field_filter}, 1, 10) <= :until)
    ORDER BY {order_by}
    LIMIT :limit OFFSET :offset
    """

    params = {
        "status": status.value if status else None,
        "since": since,
        "until": until,
        "limit": limit,
        "offset": offset,
    }

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [Task(**{**dict(r), "status": Status(r["status"])}) for r in rows]

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

        res = dict(row)
        res["status"] = Status(res["status"])
        return Task(**res)

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

        res = dict(row)
        res["status"] = Status(res["status"])
        return Task(**res)
    
@app.patch("/tasks/{task_id}", response_model=Task)
async def patch_task(task_id: uuid.UUID, request: Request):
    data = await request.json()
    allowed = {"title", "description", "status"}
    unknown = set(data) - allowed
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown fields: {sorted(unknown)}")

    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (str(task_id),)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")

        current = dict(row)

        if "status" in data:
            try:
                data["status"] = Status(data["status"]).value
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status")

        merged = {**current, **data}

        try:
            validated = TaskInput.model_validate({
                "title": merged["title"],
                "description": merged.get("description"),
                "status": Status(merged["status"]),
            })
        except ValidationError as e:
            raise RequestValidationError(e.errors())

        now = now_utc_iso()
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (validated.title, validated.description, validated.status.value, now, str(task_id)),
        )

        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (str(task_id),)).fetchone()
        res = dict(row)
        res["status"] = Status(res["status"])
        return Task(**res)