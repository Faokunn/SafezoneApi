from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base

class IncidentReport(Base):
    __tablename__ = 'incident_reports'
    id = Column(Integer, primary_key=True)
    dangerZone_id = Column(Integer, ForeignKey('danger_zones.id'), nullable=False)
    description = Column(Text, nullable=False)
    report_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    danger_zone = relationship("DangerZone", back_populates="incident_reports")
