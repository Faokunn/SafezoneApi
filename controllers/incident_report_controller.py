from fastapi import APIRouter, HTTPException, status
from typing import List
from schemas.incident_report_schema import IncidentReportModel, IncidentReportBase, IncidentReportRequestModel
from database.db_setup import db_dependency
from services.incident_report_service import (
    get_all_incidents,
    create_incident_report_service,
    update_incident_report_service,
    delete_incident_report_service,
    get_incident_report_by_id_service
)

router = APIRouter()

@router.get("/incident-reports/", response_model=List[IncidentReportBase])
async def get_incident_reports(db: db_dependency):
    return await get_all_incidents(db)

@router.get("/get-incident-report/{incident_id}", response_model=IncidentReportModel)
async def get_incident_report(incident_id: int, db: db_dependency):
    incident = await get_incident_report_by_id_service(incident_id, db)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident report not found")
    return incident

@router.post("/create-incident-report/")
async def create_incident_report(request_data: IncidentReportRequestModel, db: db_dependency):
    return await create_incident_report_service(request_data, db)

@router.put("/update-incident-report/{incident_id}")
async def update_incident_report(incident_id: int, request_data: IncidentReportRequestModel, db: db_dependency):
    updated_report = await update_incident_report_service(incident_id, request_data, db)
    if not updated_report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident report not found for update")
    return updated_report

@router.delete("/delete-incident-report/{incident_id}")
async def delete_incident_report(incident_id: int, db: db_dependency):
    result = await delete_incident_report_service(incident_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident report not found for deletion")
    return result
