from sqlalchemy import Column, Integer, String, DateTime, func
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    google_sub = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True)
    picture_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
