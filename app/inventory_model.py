from sqlalchemy import Column, Integer, String, Date, DateTime, func, ForeignKey
from .db import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    location = Column(String, nullable=False, default="pantry")  # pantry/fridge/freezer
    category = Column(String, nullable=True)
    purchase_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
