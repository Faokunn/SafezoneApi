from pydantic import BaseModel
from schemas import danger_zone_schema
from typing import List, Optional
from datetime import datetime, date, time

class IncidentReportModel(BaseModel):
    id: int
    danger_zone_id: int
    description: str
    report_date: date
    report_time: time
    images: Optional[List[str]] = None
    report_timestamp: datetime
    status: Optional[str]
    updated_at: datetime

    class Config:
        orm_mode = True

class IncidentReportBase(BaseModel):
    incident_report: IncidentReportModel
    danger_zone: danger_zone_schema.DangerZoneModel

    class Config:
        orm_mode = True

class IncidentReportRequestModel(BaseModel):
    danger_zone_id: int
    description: str
    report_date: date
    report_time: time
    images: Optional[List[str]] = None
    report_timestamp: datetime
    status: str
    updated_at: datetime
    latitude: float
    longitude: float
    radius: float
    name: str

    class Config:
        orm_mode = True