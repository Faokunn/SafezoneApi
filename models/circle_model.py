from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class Circle(Base):
    __tablename__ = 'circle'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="circle")