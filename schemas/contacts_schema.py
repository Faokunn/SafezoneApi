from pydantic import BaseModel

class ContactSchema(BaseModel):
    phone_number: int
    name: str

    class Config:
        from_attributes=True

class ContactResponse(BaseModel):
    contact: ContactSchema
    class Config:
        orm_mode = True