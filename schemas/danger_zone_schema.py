from pydantic import BaseModel

class DangerZoneModel(BaseModel):
    id: int
    is_verified: bool
    latitude: float
    longitude: float
    radius: float
    name: str

    class Config:
        orm_mode=True
        from_attributes=True