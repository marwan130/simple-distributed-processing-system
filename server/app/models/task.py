from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(String)
    result = Column(String, nullable=True)
    completed = Column(Boolean, default=False)