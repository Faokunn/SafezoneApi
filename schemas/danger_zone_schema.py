from pydantic import BaseModel

class DangerZoneModel(BaseModel):
    id: int
    is_verified: bool
    latitude: float
    longitude: float
    radius: float
    name: str

    class Config:
        from_attributes=True