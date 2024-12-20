from pydantic import BaseModel

class ProfileModel(BaseModel):
    address: str
    is_admin: bool = False
    is_girl: bool = True
    is_verified: bool = False