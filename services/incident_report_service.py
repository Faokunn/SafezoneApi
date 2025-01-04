from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from models.incidentreport_model import IncidentReport
from models.dangerzone_model import DangerZone
from models.user_model import User
from schemas.incident_report_schema import IncidentReportModel, IncidentReportBase, IncidentReportRequestModel
from schemas.danger_zone_schema import DangerZoneModel
from fastapi import HTTPException, UploadFile
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from firebase_admin import credentials, initialize_app, storage
from sqlalchemy.ext.asyncio import AsyncSession


async def handle_exception(e: Exception):
    if isinstance(e, HTTPException):
        raise e
    raise HTTPException(status_code=500, detail=str(e))

def parse_report_timestamp(timestamp):
    try:
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Manila"))
        return timestamp.astimezone(ZoneInfo("Asia/Manila"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid report_timestamp: {str(e)}")

async def get_or_create_danger_zone(db, latitude, longitude, radius, name, danger_zone_id=None):
    if danger_zone_id:
        danger_zone = await db.execute(select(DangerZone).filter_by(id=danger_zone_id))
        danger_zone = danger_zone.scalar()
        if not danger_zone:
            raise HTTPException(status_code=404, detail="Danger Zone not found.")
    else:
        result = await db.execute(
            select(DangerZone).filter(DangerZone.latitude == latitude, DangerZone.longitude == longitude)
        )
        danger_zone = result.scalar()
        if not danger_zone:
            danger_zone = DangerZone(
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                name=name,
                is_verified=False
            )
            db.add(danger_zone)
            await db.commit()
    return danger_zone

async def get_all_incidents(db):
    try:
        result = await db.execute(select(IncidentReport).options(selectinload(IncidentReport.danger_zone)))
        incidents = result.scalars().all()

        response = [{
            "incident_report": IncidentReportModel(
                id=incident.id,
                user_id=incident.user_id,
                danger_zone_id=incident.danger_zone_id,
                description=incident.description,
                report_date=incident.report_date,
                report_time=incident.report_time,
                status=incident.status,
                images=incident.images,
                report_timestamp=incident.report_timestamp,
                updated_at=incident.updated_at
            ),
            "danger_zone": DangerZoneModel(
                id=incident.danger_zone.id,
                is_verified=incident.danger_zone.is_verified,
                latitude=incident.danger_zone.latitude,
                longitude=incident.danger_zone.longitude,
                radius=incident.danger_zone.radius,
                name=incident.danger_zone.name,
            )
        } for incident in incidents]

        return response

    except Exception as e:
        await handle_exception(e)

async def create_incident_report_service(request_data, db):
    try:
        user_result = await db.execute(select(User).filter_by(id=request_data.user_id))
        user = user_result.scalar()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        report_timestamp = parse_report_timestamp(request_data.report_timestamp)
        danger_zone = await get_or_create_danger_zone(
            db, 
            request_data.latitude, 
            request_data.longitude, 
            request_data.radius, 
            request_data.name, 
            danger_zone_id=request_data.danger_zone_id
        )

        current_time = datetime.now(ZoneInfo("Asia/Manila"))
        incident_report = IncidentReport(
            user_id=request_data.user_id, 
            danger_zone_id=danger_zone.id,
            description=request_data.description,
            report_date=request_data.report_date,
            report_time=request_data.report_time,
            images=request_data.images or [],
            report_timestamp=report_timestamp,
            updated_at=current_time
        )

        db.add(incident_report)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error creating incident report: {str(e)}")

        return {
            "message": "Incident report created successfully",
            "incident_report_id": incident_report.id,
            "is_verified": danger_zone.is_verified
        }

    except Exception as e:
        await handle_exception(e)

##### To test req sa app yung image upload

# async def upload_images_to_firebase(files: List[UploadFile]) -> List[str]:
#     uploaded_urls = []
#     for file in files:
#         if not file.filename.endswith((".jpg", ".jpeg", ".png")):
#             raise HTTPException(status_code=400, detail=f"File {file.filename} must be an image")
        
#         bucket = storage.bucket()
#         blob = bucket.blob(file.filename)
#         blob.upload_from_string(await file.read(), content_type=file.content_type)
#         uploaded_urls.append(blob.public_url)
    
#     return uploaded_urls

# async def create_incident_report_service(request_data, db):
#     try:
#         report_timestamp = parse_report_timestamp(request_data.report_timestamp)
        
#         danger_zone = await get_or_create_danger_zone(
#             db, 
#             request_data.latitude, 
#             request_data.longitude, 
#             request_data.radius, 
#             request_data.name, 
#             danger_zone_id=request_data.danger_zone_id
#         )
        
#         uploaded_image_urls = await upload_images_to_firebase(request_data.images or [])

#         current_time = datetime.now(ZoneInfo("Asia/Manila"))
#         incident_report = IncidentReport(
#             danger_zone_id=danger_zone.id,
#             description=request_data.description,
#             report_date=request_data.report_date,
#             report_time=request_data.report_time,
#             images=uploaded_image_urls, 
#             report_timestamp=report_timestamp,
#             updated_at=current_time
#         )

#         db.add(incident_report)
#         try:
#             await db.commit()
#         except IntegrityError as e:
#             await db.rollback()
#             raise HTTPException(status_code=400, detail=f"Error creating incident report: {str(e)}")

#         return {
#             "message": "Incident report created successfully",
#             "incident_report_id": incident_report.id,
#             "is_verified": danger_zone.is_verified
#         }

#     except Exception as e:
#         await handle_exception(e)

async def update_incident_report_service(incident_id: int, update_data, db):
    try:
        result = await db.execute(select(IncidentReport).filter_by(id=incident_id))
        incident_report = result.scalar()

        if not incident_report:
            raise HTTPException(status_code=404, detail="Incident report not found.")

        if update_data.description:
            incident_report.description = update_data.description
        if update_data.report_date:
            incident_report.report_date = update_data.report_date
        if update_data.report_time:
            incident_report.report_time = update_data.report_time
        if update_data.images:
            incident_report.images = update_data.images
        if update_data.report_timestamp:
            incident_report.report_timestamp = parse_report_timestamp(update_data.report_timestamp)
        if update_data.status:
            incident_report.status = update_data.status

        if update_data.danger_zone_id:
            danger_zone = await db.execute(select(DangerZone).filter_by(id=update_data.danger_zone_id))
            danger_zone = danger_zone.scalar()
            if not danger_zone:
                raise HTTPException(status_code=404, detail="Danger Zone not found.")
            incident_report.danger_zone_id = danger_zone.id

        incident_report.updated_at = datetime.now(ZoneInfo("Asia/Manila"))

        db.add(incident_report)
        await db.commit()

        return {
            "message": "Incident report updated successfully.",
            "incident_report": IncidentReportModel.from_orm(incident_report)
        }

    except Exception as e:
        await db.rollback()
        await handle_exception(e)

async def delete_incident_report_service(incident_id: int, db):
    try:
        result = await db.execute(select(IncidentReport).filter_by(id=incident_id))
        incident_report = result.scalar()

        if not incident_report:
            raise HTTPException(status_code=404, detail="Incident report not found.")

        await db.delete(incident_report)
        await db.commit()

        return {"message": f"Incident report {incident_id} deleted successfully."}

    except Exception as e:
        await db.rollback()
        await handle_exception(e)

async def get_incident_report_by_id_service(incident_id: int, db):
    try:
        result = await db.execute(select(IncidentReport).filter(IncidentReport.id == incident_id))
        incident_report = result.scalars().first()
        if not incident_report:
            raise HTTPException(status_code=404, detail="Incident report not found.")
        return incident_report

    except Exception as e:
        await handle_exception(e)

async def get_incident_report_by_danger_zone_id_service(danger_zone_id: int, db):
    try:
        result = await db.execute(
            select(IncidentReport)
            .where(IncidentReport.danger_zone_id == danger_zone_id)
            .options(selectinload(IncidentReport.danger_zone))
        )
        incidents = result.scalars().all()

        response = [{
            "incident_report": IncidentReportModel(
                id=incident.id,
                user_id=incident.user_id,
                danger_zone_id=incident.danger_zone_id,
                description=incident.description,
                report_date=incident.report_date,
                report_time=incident.report_time,
                status=incident.status,
                images=incident.images,
                report_timestamp=incident.report_timestamp,
                updated_at=incident.updated_at
            ),
            "danger_zone": DangerZoneModel(
                id=incident.danger_zone.id,
                is_verified=incident.danger_zone.is_verified,
                latitude=incident.danger_zone.latitude,
                longitude=incident.danger_zone.longitude,
                radius=incident.danger_zone.radius,
                name=incident.danger_zone.name,
            )
        } for incident in incidents]

        return response


    except Exception as e:
        await handle_exception(e)

async def get_incident_report_by_status_service(status: str, db):
    try:
        result = await db.execute(
            select(IncidentReport)
            .where(IncidentReport.status == status)
            .options(selectinload(IncidentReport.danger_zone))
        )
        incidents = result.scalars().all()

        response = [{
            "incident_report": IncidentReportModel(
                id=incident.id,
                user_id=incident.user_id,
                danger_zone_id=incident.danger_zone_id,
                description=incident.description,
                report_date=incident.report_date,
                report_time=incident.report_time,
                status=incident.status,
                images=incident.images,
                report_timestamp=incident.report_timestamp,
                updated_at=incident.updated_at
            ),
            "danger_zone": DangerZoneModel(
                id=incident.danger_zone.id,
                is_verified=incident.danger_zone.is_verified,
                latitude=incident.danger_zone.latitude,
                longitude=incident.danger_zone.longitude,
                radius=incident.danger_zone.radius,
                name=incident.danger_zone.name,
            )
        } for incident in incidents]

        return response

    except Exception as e:
        await handle_exception(e)

async def get_incident_report_by_user_id_service(user_id: int, db):
    try:
        result = await db.execute(
            select(IncidentReport)
            .where(IncidentReport.user_id == user_id)
            .options(selectinload(IncidentReport.danger_zone))
        )
        incidents = result.scalars().all()

        response = [{
            "incident_report": IncidentReportModel(
                id=incident.id,
                user_id=incident.user_id,
                danger_zone_id=incident.danger_zone_id,
                description=incident.description,
                report_date=incident.report_date,
                report_time=incident.report_time,
                status=incident.status,
                images=incident.images,
                report_timestamp=incident.report_timestamp,
                updated_at=incident.updated_at
            ),
            "danger_zone": DangerZoneModel(
                id=incident.danger_zone.id,
                is_verified=incident.danger_zone.is_verified,
                latitude=incident.danger_zone.latitude,
                longitude=incident.danger_zone.longitude,
                radius=incident.danger_zone.radius,
                name=incident.danger_zone.name,
            )
        } for incident in incidents]

        return response

    except Exception as e:
        await handle_exception(e)