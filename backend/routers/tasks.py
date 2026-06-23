from fastapi import APIRouter, HTTPException, Depends, status

import database
import schemas
import auth


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    current_user: dict = Depends(auth.get_current_user)
):
    task_id = database.create_task(
        task.title,
        task.description,
        task.priority,
        task.due_date,
        current_user["email"]
    )

    return database.get_task_by_id(task_id)


@router.get("/", response_model=list[schemas.TaskResponse])
def get_tasks(
    status: str = None,
    priority: str = None,
    current_user: dict = Depends(auth.get_current_user)
):
    return database.get_filtered_tasks(
        current_user["email"],
        status,
        priority
    )


@router.get("/summary")
def get_summary(current_user: dict = Depends(auth.get_current_user)):
    return database.get_task_summary(current_user["email"])


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    current_user: dict = Depends(auth.get_current_user)
):
    task = database.get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["owner_email"] != current_user["email"]:
        raise HTTPException(status_code=403, detail="You are not allowed to access this task")

    return task


@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_data: schemas.TaskUpdate,
    current_user: dict = Depends(auth.get_current_user)
):
    task = database.get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["owner_email"] != current_user["email"]:
        raise HTTPException(status_code=403, detail="You are not allowed to update this task")

    database.update_task(
        task_id,
        task_data.title,
        task_data.description,
        task_data.priority,
        task_data.due_date
    )

    return database.get_task_by_id(task_id)


@router.patch("/{task_id}/status", response_model=schemas.TaskResponse)
def change_status(
    task_id: int,
    status_data: schemas.StatusUpdate,
    current_user: dict = Depends(auth.get_current_user)
):
    task = database.get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["owner_email"] != current_user["email"]:
        raise HTTPException(status_code=403, detail="You are not allowed to update this task")

    database.update_task_status(task_id, status_data.status)

    return database.get_task_by_id(task_id)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: dict = Depends(auth.get_current_user)
):
    task = database.get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["owner_email"] != current_user["email"]:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this task")

    database.delete_task(task_id)

    return {"message": "Task deleted successfully"}