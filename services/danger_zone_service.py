from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from models.dangerzone_model import DangerZone
from schemas.danger_zone_schema import DangerZoneModel
from fastapi import HTTPException

async def get_danger_zone_by_id_service(danger_zone_id: int, db):
    try:
        result = await db.execute(select(DangerZone).filter(DangerZone.id == danger_zone_id))
        danger_zone = result.scalars().first() 
        if not danger_zone:
            raise HTTPException(status_code=404, detail="Danger zone not found.")
        return danger_zone

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving danger zone: {str(e)}")
    
async def get_all_danger_zones_service(db):
    try:
        result = await db.execute(select(DangerZone).options(selectinload(DangerZone.incident_reports)))
        danger_zones = result.scalars().all()

        return [
            {
                "danger_zone": DangerZoneModel.from_orm(danger_zone)  
            }
            for danger_zone in danger_zones
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving danger zones: {str(e)}")
    
## get all verified danger zones
