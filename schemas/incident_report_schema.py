from pydantic import BaseModel
from schemas import danger_zone_schema
from typing import List, Optional
from datetime import datetime

class IncidentReportModel(BaseModel):
    danger_zone_id: int
    description: str
    images: Optional[List[str]] = None
    report_time: datetime

    class Config:
        orm_mode = True

class IncidentReportResponse(BaseModel):
    incident_report: IncidentReportModel
    danger_zone: danger_zone_schema.DangerZoneModel

    class Config:
        orm_mode = True

