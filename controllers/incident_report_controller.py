from fastapi import APIRouter, HTTPException, status, UploadFile, File, FastAPI
from dotenv import load_dotenv
import os
from firebase_admin import credentials, initialize_app, storage
from datetime import timedelta
from typing import List, Optional
from schemas.incident_report_schema import IncidentReportModel, IncidentReportBase, IncidentReportRequestModel
from database.db_setup import db_dependency
from services.incident_report_service import (
    get_all_incidents,
    create_incident_report_service,
    update_incident_report_service,
    delete_incident_report_service,
    get_incident_report_by_id_service,
    get_incident_report_by_danger_zone_id_service,
    get_incident_report_by_status_service,
    get_incident_report_by_user_id_service
)

load_dotenv()

cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')

cred = credentials.Certificate(cred_path)
firebase_app = initialize_app(cred, {
    'storageBucket': storage_bucket
})

router = APIRouter()

## GET ROUTES

@router.get("/incident-reports/", response_model=List[IncidentReportBase])
async def get_incident_reports(db: db_dependency):
    return await get_all_incidents(db)

@router.get("/get-incident-report/{incident_id}", response_model=IncidentReportModel)
async def get_incident_report(incident_id: int, db: db_dependency):
    incident = await get_incident_report_by_id_service(incident_id, db)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident report not found")
    return incident

@router.get("/get-incident-reports/{danger_zone_id}")
async def get_incident_report_by_danger_zone_id(danger_zone_id: int, db: db_dependency):
    incident = await get_incident_report_by_danger_zone_id_service(danger_zone_id, db)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident reports not found")
    return incident

@router.get("/get-incident-reports-status/{status}")
async def get_incident_report_by_status(status: str, db: db_dependency):
    incident = await get_incident_report_by_status_service(status, db)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident reports not found")
    return incident

@router.get("/get-incident-reports-user/{user_id}")
async def get_incident_report_by_user_id(user_id: int, db: db_dependency):
    incident = await get_incident_report_by_user_id_service(user_id, db)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident reports not found")
    return incident

## POST ROUTES

@router.post("/create-incident-report/")
async def create_incident_report(request_data: IncidentReportRequestModel, db: db_dependency):
    return await create_incident_report_service(request_data, db)

## PUT ROUTES

@router.put("/update-incident-report/{incident_id}")
async def update_incident_report(incident_id: int, request_data: IncidentReportRequestModel, db: db_dependency):
    updated_report = await update_incident_report_service(incident_id, request_data, db)
    if not updated_report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident report not found for update")
    return updated_report

## DELETE ROUTES

@router.delete("/delete-incident-report/{incident_id}")
async def delete_incident_report(incident_id: int, db: db_dependency):
    result = await delete_incident_report_service(incident_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident report not found for deletion")
    return result

## TEST ROUTES

@router.post("/upload")
async def create_upload_file(file: UploadFile = File(...), path: Optional[str] = None):
    if not file.filename.endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="File must be an image")
    if not path:
        path = file.filename
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(await file.read(), content_type=file.content_type)


    url = blob.public_url
    return {"url": url}