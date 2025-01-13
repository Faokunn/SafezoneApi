from pydantic import BaseModel

class ProfileModel(BaseModel):
    address: str
    first_name: str
    last_name: str
    is_admin: bool = False
    is_girl: bool = True
    is_verified: bool = False