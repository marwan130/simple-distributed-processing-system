from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(String)
    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        server_default=TaskStatus.PENDING.value
    )
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    worker_id = Column(String, nullable=True)

class Worker(Base):
    __tablename__ = "workers"

    id = Column(String, primary_key=True)
    status = Column(String, default="active")
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    current_task_id = Column(Integer, nullable=True) 