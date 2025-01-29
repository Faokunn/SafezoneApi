from models.contacts_model import ContactModel
from sqlalchemy.future import select

async def create_contact(db, user_id, contact: ContactModel):
    new_contact = ContactModel(user_id=user_id, **contact.dict())
    db.add(new_contact)
    await db.commit()
    return new_contact

async def update_contact(db, id, contact: ContactModel):
    contact_to_update = await db.get(ContactModel, id)
    if contact_to_update:
        contact_to_update.update_from_dict(contact.dict())
        await db.commit()
        return contact_to_update
    return None

async def delete_contact(db, id: int):
    contact_to_delete = await db.get(ContactModel, id)
    if contact_to_delete:
        print(f"Found contact: {contact_to_delete.name}, ID: {contact_to_delete.id}")
        
        try:
            await db.delete(contact_to_delete)
            await db.commit()
            print(f"Successfully deleted contact with ID {id}")
            return True
        except Exception as e:
            print(f"Error during commit: {e}")
            await db.rollback()  # Rollback if an error occurs
            return False
    else:
        print(f"Contact with ID {id} not found.")
        return False

async def get_all_user_contacts(db, user_id):
    result = await db.execute(select(ContactModel).filter(ContactModel.user_id == user_id))
    return result.scalars().all()
