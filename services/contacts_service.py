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

async def delete_contact(db, id):
    contact_to_delete = await db.get(ContactModel, id)
    if contact_to_delete:
        db.delete(contact_to_delete)
        await db.commit()
        return True
    return False

async def get_all_user_contacts(db, user_id):
    result = await db.execute(select(ContactModel).filter(ContactModel.user_id == user_id))
    return result.scalars().all()
