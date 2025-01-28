from pydantic import BaseModel

class CircleSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True 
class CircleResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        orm_mode = True