from sqlalchemy.future import select
from models import user_model, profile_model, contacts_model
from fastapi import HTTPException, status
import bcrypt
from schemas.user_schema import UserModel, UserProfileResponse
from schemas.profile_schema import ProfileModel
from schemas.contacts_schema import ContactSchema
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

async def get_user_by_email(db, email):
    result = await db.execute(select(user_model.User).filter(user_model.User.email == email))
    return result.scalars().first()

async def get_all_users(db):
    result = await db.execute(select(user_model.User))
    return result.scalars().all()

async def login_user(db, email, password):
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found: Please register"
        )
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    return UserModel(
        username=user.username,
        email=user.email,
        password="*****",
    )

async def create_user(user: user_model.User, profile: profile_model.Profile, db):
    # Check if the user already exists by email
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        hashed_password = get_password_hash(user.password)

        # Create the new user
        new_user = user_model.User(
            username=user.username,
            email=user.email,
            password=hashed_password,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        new_profile = profile_model.Profile(
            user_id=new_user.id,
            address=profile.address,
            first_name=profile.first_name,
            last_name=profile.last_name,
            is_admin=profile.is_admin,
            is_girl=profile.is_girl,
            is_verified=profile.is_verified,
        )
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_profile)

        default_contacts = [
            contacts_model.ContactModel(
                user_id=new_user.id,
                phone_number="117",
                name="Philippine National Police (PNP)",
            ),
            contacts_model.ContactModel(
                user_id=new_user.id,
                phone_number="911", 
                name="Ambulance",
            ),
            contacts_model.ContactModel(
                user_id=new_user.id,
                phone_number="160", 
                name="Firefighter",
            )
        ]

        # Add the default contacts to the DB
        db.add_all(default_contacts)
        await db.commit()

        return {
            "user": user_model.User(
                username=new_user.username,
                email=new_user.email,
                password="*****",  # Don't return the password for security
            ),
            "profile": profile_model.Profile(
                address=new_profile.address,
                first_name=new_profile.first_name,
                last_name=new_profile.last_name,
                is_admin=new_profile.is_admin,
                is_girl=new_profile.is_girl,
                is_verified=new_profile.is_verified,
            ),
            "contacts": [
                contacts_model.ContactModel(
                    phone_number=contact.phone_number,
                    name=contact.name,
                ) for contact in default_contacts
            ],
        }

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )