from sqlalchemy import Column, Integer, String, ForeignKey
from .db import Base

class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), index=True, nullable=False)

    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
