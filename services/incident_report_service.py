from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from models.incidentreport_model import IncidentReport
from models.dangerzone_model import DangerZone
from schemas.incident_report_schema import IncidentReportModel, IncidentReportBase
from schemas.danger_zone_schema import DangerZoneModel
from fastapi import HTTPException
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.exc import IntegrityError

async def get_all_incidents(db):
    try:
        result = await db.execute(select(IncidentReport).options(selectinload(IncidentReport.danger_zone)))
        incidents = result.scalars().all()

        response = []
        for incident in incidents:
            response.append({
                "incident_report": IncidentReportModel(
                    id=incident.id,
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
                    is_verified=incident.danger_zone.is_verified,
                    latitude=incident.danger_zone.latitude,
                    longitude=incident.danger_zone.longitude,
                    radius=incident.danger_zone.radius,
                    name=incident.danger_zone.name,
                )
            })
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving incidents: {str(e)}")


async def create_incident_report_service(request_data, db):
    try:
        if isinstance(request_data.report_timestamp, str):
            parsed_time = datetime.fromisoformat(request_data.report_timestamp.replace("Z", "+00:00"))
        else:
            parsed_time = request_data.report_timestamp

        report_timestamp = parsed_time.astimezone(ZoneInfo("Asia/Manila"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid report_timestamp: {str(e)}")

    if request_data.danger_zone_id > 0:
        danger_zone = await db.execute(select(DangerZone).filter_by(id=request_data.danger_zone_id))
        danger_zone = danger_zone.scalar()
        if not danger_zone:
            raise HTTPException(status_code=404, detail="Danger Zone not found.")
    else:
        result = await db.execute(
            select(DangerZone).filter(
                DangerZone.latitude == request_data.latitude, 
                DangerZone.longitude == request_data.longitude
            )
        )
        danger_zone = result.scalar()

        if not danger_zone:
            danger_zone = DangerZone(
                latitude=request_data.latitude,
                longitude=request_data.longitude,
                radius=request_data.radius,
                name=request_data.name,
                is_verified=False
            )
            db.add(danger_zone)
            await db.commit()

    current_time = datetime.now(ZoneInfo("Asia/Manila"))
    incident_report = IncidentReport(
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

    return {"message": "Incident report created successfully", "incident_report_id": incident_report, "status": danger_zone.is_verified}

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
            parsed_time = (
                datetime.fromisoformat(update_data.report_timestamp.replace("Z", "+00:00"))
                if isinstance(update_data.report_timestamp, str)
                else update_data.report_timestamp
            )
            incident_report.report_timestamp = parsed_time.astimezone(ZoneInfo("Asia/Manila"))
        if update_data.status:
            incident_report.status = update_data.status

        if update_data.danger_zone_id:
            danger_zone_result = await db.execute(select(DangerZone).filter_by(id=update_data.danger_zone_id))
            danger_zone = danger_zone_result.scalar()

            if not danger_zone:
                raise HTTPException(status_code=404, detail="Danger Zone not found.")
            
            incident_report.danger_zone_id = danger_zone.id

        incident_report.updated_at = datetime.now(ZoneInfo("Asia/Manila"))

        db.add(incident_report)
        await db.commit()

        return {
            "message": "Incident report updated successfully.",
            "incident_report": {
                "id": incident_report.id,
                "danger_zone_id": incident_report.danger_zone_id,
                "description": incident_report.description,
                "report_date": incident_report.report_date,
                "report_time": incident_report.report_time,
                "images": incident_report.images,
                "report_timestamp": incident_report.report_timestamp.isoformat(),
                "status": incident_report.status,
                "updated_at": incident_report.updated_at.isoformat(),
            },
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating incident report: {str(e)}")

async def delete_incident_report_service(incident_id: int, db):
    try:
        result = await db.execute(select(IncidentReport).filter_by(id=incident_id))
        incident_report = result.scalar()

        if not incident_report:
            raise HTTPException(status_code=404, detail="Incident report not found.")

        await db.delete(incident_report)
        await db.commit()

        return {
            "message": f"Incident report deleted successfully. {incident_id}",
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting incident report: {str(e)}")