from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Dict
from ..db import get_db
from ..models import Task, TaskStatus, Worker
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

class TaskCreate(BaseModel):
    input_data: str

class TaskResponse(BaseModel):
    id: int
    input_data: str
    status: str
    result: dict | None
    created_at: datetime
    updated_at: datetime
    worker_id: str | None

    class Config:
        from_attributes = True

@router.post("/workers/{worker_id}/heartbeat")
async def worker_heartbeat(worker_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Worker).filter(Worker.id == worker_id))
    worker = result.scalar_one_or_none()
    
    if worker is None:
        worker = Worker(id=worker_id)
        db.add(worker)
    
    worker.last_heartbeat = datetime.utcnow()
    await db.commit()
    return {"status": "success"}

@router.get("/workers/count")
async def get_active_workers(db: AsyncSession = Depends(get_db)):
    # remove inactive workers who dont have a heartbeat for 30 seconds
    cutoff_time = datetime.utcnow() - timedelta(seconds=30)
    await db.execute(
        delete(Worker).where(Worker.last_heartbeat < cutoff_time)
    )
    await db.commit()
    
    # count remaining active workers
    result = await db.execute(select(Worker))
    workers = result.scalars().all()
    return {"count": len(workers)}

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(
        input_data=task.input_data,
        status=TaskStatus.PENDING,
        result=None,
        worker_id=None
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).order_by(Task.created_at.desc()))
    tasks = result.scalars().all()
    return tasks

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks/{task_id}/claim")
async def claim_task(task_id: int, worker_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail="Task is not available")
    
    task.status = TaskStatus.PROCESSING
    task.worker_id = worker_id
    await db.commit()
    return {"status": "success"}

@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    worker_id: str,
    task_result: Dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.worker_id != worker_id:
        raise HTTPException(status_code=403, detail="Task belongs to another worker")
    
    task.status = TaskStatus.COMPLETED
    task.result = task_result
    await db.commit()
    return {"status": "success"}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.execute(delete(Task).where(Task.id == task_id))
    await db.commit()
    return {"status": "success", "message": f"Task {task_id} deleted"}

@router.delete("/tasks/clear-completed")
async def clear_completed_tasks(db: AsyncSession = Depends(get_db)):
    try:
        print("Attempting to clear completed tasks...")
        result = await db.execute(select(Task).where(Task.status == TaskStatus.COMPLETED))
        completed_tasks = result.scalars().all()
        
        if not completed_tasks:
            print("No completed tasks found")
            return {"status": "success", "message": "No completed tasks to clear"}

        print(f"Found {len(completed_tasks)} completed tasks to clear")
        # Delete completed tasks
        await db.execute(delete(Task).where(Task.status == TaskStatus.COMPLETED))
        await db.commit()
        print(f"Successfully cleared {len(completed_tasks)} tasks")
        return {"status": "success", "message": f"Cleared {len(completed_tasks)} completed tasks"}
    except Exception as e:
        print(f"Error clearing tasks: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))