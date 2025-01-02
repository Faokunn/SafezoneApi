from sqlalchemy.future import select
from models.incidentreport_model import IncidentReport
from models.dangerzone_model import DangerZone
from fastapi import HTTPException
from datetime import datetime
from zoneinfo import ZoneInfo

async def verify_incident_report_service(db, incident_id: int):
    try:
        result = await db.execute(select(IncidentReport).filter_by(id=incident_id))
        incident_report = result.scalar()

        if not incident_report:
            raise HTTPException(status_code=404, detail="Incident report not found.")

        incident_report.status = "verified"
        incident_report.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
        db.add(incident_report)

        danger_zone_data = None
        if incident_report.danger_zone_id:
            result = await db.execute(select(DangerZone).filter_by(id=incident_report.danger_zone_id))
            danger_zone = result.scalar()

            if danger_zone:
                danger_zone.is_verified = True
                danger_zone.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
                db.add(danger_zone)

                danger_zone_data = {
                    "id": danger_zone.id,
                    "is_verified": danger_zone.is_verified,
                    "updated_at": danger_zone.updated_at.isoformat(),
                }
            else:
                raise HTTPException(status_code=404, detail="Associated Danger Zone not found.")

        await db.commit()

        return {
            "message": f"Incident report {incident_id} verified.",
            "incident_report": {
                "id": incident_report.id,
                "status": incident_report.status,
                "updated_at": incident_report.updated_at.isoformat(),
            },
            "danger_zone": danger_zone_data,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error verifying incident report: {str(e)}")




async def reject_incident_report_service(db, incident_id: int):
    try:
        result = await db.execute(select(IncidentReport).filter_by(id=incident_id))
        incident_report = result.scalar()

        if not incident_report:
            raise HTTPException(status_code=404, detail="Incident report not found.")

        incident_report.status = "rejected"
        incident_report.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
        db.add(incident_report)

        danger_zone_data = None
        if incident_report.danger_zone_id:
            result = await db.execute(select(DangerZone).filter_by(id=incident_report.danger_zone_id))
            danger_zone = result.scalar()

            if danger_zone:
                danger_zone.is_verified = False
                danger_zone.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
                db.add(danger_zone)

                danger_zone_data = {
                    "id": danger_zone.id,
                    "is_verified": danger_zone.is_verified,
                    "updated_at": danger_zone.updated_at.isoformat(),
                }
            else:
                raise HTTPException(status_code=404, detail="Associated Danger Zone not found.")

        await db.commit()

        return {
            "message": f"Incident report {incident_id} rejected.",
            "incident_report": {
                "id": incident_report.id,
                "status": incident_report.status,
                "updated_at": incident_report.updated_at.isoformat(),
            },
            "danger_zone": danger_zone_data,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error verifying incident report: {str(e)}")

async def under_review_incident_report_service(db, incident_id: int):
    try:
        result = await db.execute(select(IncidentReport).filter_by(id=incident_id))
        incident_report = result.scalar()

        if not incident_report:
            raise HTTPException(status_code=404, detail="Incident report not found.")

        incident_report.status = "under review"
        incident_report.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
        db.add(incident_report)

        danger_zone_data = None
        if incident_report.danger_zone_id:
            result = await db.execute(select(DangerZone).filter_by(id=incident_report.danger_zone_id))
            danger_zone = result.scalar()

            if danger_zone:
                danger_zone.is_verified = False
                danger_zone.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
                db.add(danger_zone)

                danger_zone_data = {
                    "id": danger_zone.id,
                    "is_verified": danger_zone.is_verified,
                    "updated_at": danger_zone.updated_at.isoformat(),
                }
            else:
                raise HTTPException(status_code=404, detail="Associated Danger Zone not found.")


        await db.commit()

        return {
            "message": f"Incident report {incident_id} is under review.",
            "incident_report": {
                "id": incident_report.id,
                "status": incident_report.status,
                "updated_at": incident_report.updated_at.isoformat(),
            },
            "danger_zone": danger_zone_data,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error verifying incident report: {str(e)}")
    
## TODO: get incident report by id 