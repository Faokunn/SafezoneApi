from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class IncidentReport(Base):
    __tablename__ = 'incident_reports'
    id = Column(Integer, primary_key=True)
    danger_zone_id = Column(Integer, ForeignKey('danger_zones.id'), nullable=False)
    description = Column(Text, nullable=False)
    images = Column(JSON, nullable=True)
    report_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    danger_zone = relationship("DangerZone", back_populates="incident_reports")
