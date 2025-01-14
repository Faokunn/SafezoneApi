from pydantic import BaseModel
from schemas import profile_schema

class UserModel(BaseModel):
    id: int
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

class UserProfileResponse(BaseModel):
    user: UserModel
    profile: profile_schema.ProfileModel

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    username: str
    email: str
    profile: profile_schema.ProfileModel

    class Config:
        orm_mode = True