from pydantic import BaseModel

class DangerZoneModel(BaseModel):
    is_verified: bool
    latitude: float
    longitude: float
    radius: float
    name: str