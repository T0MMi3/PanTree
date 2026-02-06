from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text
from .db import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    source = Column(String, nullable=False, default="paste")  # paste/upload/etc.
    raw_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
