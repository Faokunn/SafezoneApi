from fastapi import APIRouter
from database.db_setup import db_dependency
from services.danger_zone_service import get_all_danger_zones_service, get_danger_zone_by_id_service

router = APIRouter()

@router.get("/danger-zones")
async def get_danger_zones(db: db_dependency):
    danger_zones = await get_all_danger_zones_service(db)
    return danger_zones

@router.get("/get-danger-zone/{danger_zone_id}")
async def get_danger_zone_by_id(danger_zone_id: int, db: db_dependency):
    return await get_danger_zone_by_id_service(danger_zone_id, db)