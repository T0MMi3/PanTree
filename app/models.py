from sqlalchemy import Column, Integer, String, DateTime, func
from .db import Base

class Ping(Base):
    __tablename__ = "ping"
    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False, default="hello")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
