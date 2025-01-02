from fastapi import APIRouter, Depends, HTTPException
from schemas.danger_zone_schema import DangerZoneModel
from schemas.incident_report_schema import IncidentReportModel, IncidentReportBase, IncidentReportRequestModel
from database.db_setup import db_dependency
from services.incident_report_service import get_all_incidents, create_incident_report_service, update_incident_report_service, delete_incident_report_service
from typing import List

router = APIRouter()
@router.get("/incident-reports/", response_model=List[IncidentReportBase])
async def get_incident_reports(db: db_dependency):
    incidents = await get_all_incidents(db)
    return incidents

@router.post("/create-incident-report/")
async def create_incident_report(request_data: IncidentReportRequestModel, db: db_dependency):
   return await create_incident_report_service(request_data, db)

@router.put("/update-incident-report/{incident_id}")
async def update_incident_report(incident_id: int, request_data: IncidentReportRequestModel, db: db_dependency):
    try:
        updated_report = await update_incident_report_service(incident_id, request_data, db)
        return updated_report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/delete-incident-report/{incident_id}")
async def delete_incident_report(incident_id: int, db: db_dependency):
    return await delete_incident_report_service(incident_id, db)