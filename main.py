from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from db import init_db
from schemas import Status, TaskInput, Task
import tasks_service


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
) -> list[Task]:
    return tasks_service.list_tasks(
        status=status,
        date_field_filter=date_field_filter,
        since=since,
        until=until,
        sort=sort,
        direction=direction,
        limit=limit,
        offset=offset,
    )

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_input: TaskInput)-> Task:
    return tasks_service.create_task(task_input)

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: UUID):
    return tasks_service.get_task(task_id)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: UUID) -> None:
    return tasks_service.delete_task(task_id)

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: UUID, payload: TaskInput) -> Task:
    return tasks_service.update_task(task_id, payload)

@app.patch("/tasks/{task_id}", response_model=Task)
async def patch_task(task_id: UUID, request: Request) -> Task:
    return tasks_service.patch_task(task_id, await request.json())