from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.contacts_schema import ContactSchema,ContactResponse
from services.contacts_service import get_all_user_contacts,create_contact,delete_contact,update_contact
import bcrypt
from fastapi.responses import Response
from database.db_setup import db_dependency
from models.contacts_model import ContactModel
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/get-user-contacts/")
async def get_user_contacts(user_id: int, db: db_dependency):
    # Get contacts for the specified user
    contacts = await get_all_user_contacts(db, user_id)
    
    print(f"Contacts: {contacts}")

    # Prepare the response
    response = []
    for contact in contacts:
        response.append(contact)

    return response

@router.post("/create-contact/", response_model=ContactResponse)
async def create_user_contact(user_id: int, db: db_dependency, contact: ContactSchema):
    new_contact = await create_contact(db, user_id, contact)
    return ContactResponse(contact=new_contact)

@router.delete("/delete_user_contact/")
async def delete_use_contact(id: int, db: db_dependency):
    deleted_contact = await delete_contact(db, id)
    if not deleted_contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # This works for 204 No Content