from fastapi import APIRouter
from schemas.incident_report_schema import IncidentReportModel
from database.db_setup import db_dependency
from services.admin_incident_report_service import verify_incident_report_service, reject_incident_report_service, under_review_incident_report_service

router = APIRouter()

@router.put("/verify-report")
async def verify_incident_report(request_data: IncidentReportModel, db: db_dependency):
    verified_incident = await verify_incident_report_service(db, incident_id=request_data.id)
    return verified_incident

@router.put("/reject-report")
async def reject_incident_report(request_data: IncidentReportModel, db: db_dependency):
    rejected_incident = await reject_incident_report_service(db, incident_id=request_data.id)
    return rejected_incident

@router.put("/review-report")
async def review_incident_report(request_data: IncidentReportModel, db: db_dependency):
    review_incident = await under_review_incident_report_service(db, incident_id=request_data.id)
    return review_incident