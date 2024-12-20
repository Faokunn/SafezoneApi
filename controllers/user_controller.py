from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user_schema import UserModel, UserProfileResponse, LoginResponse, LoginRequest
from schemas.profile_schema import ProfileModel
from services.user_service import get_user_by_email, get_all_users,create_user,login_user
from services.profile_service import get_profile_by_user_id
import bcrypt
from database.db_setup import db_dependency
from models.profile_model import Profile
from models.user_model import User

router = APIRouter()
@router.get("/users/")
async def get_users(db: db_dependency):
    users = await get_all_users(db)
    
    response = []
    for user in users:
        user_profile = await get_profile_by_user_id(db,user.id)

        if user_profile:
            response.append({
                "user": UserModel(
                    username=user.username,
                    email=user.email,
                    password="*****",
                ),
                "profile": ProfileModel(
                    address=user_profile.address,
                    is_admin=user_profile.is_admin,
                    is_girl=user_profile.is_girl,
                    is_verified=user_profile.is_verified,
                )
            })

    return response

@router.post("/create-account/", response_model=UserProfileResponse)
async def create_usert(user: UserModel, profile: ProfileModel, db: db_dependency):
    return await create_user(user, profile, db)

@router.post("/login/", response_model=LoginResponse)
async def login(user: LoginRequest, db: db_dependency):
    user_in_db = await login_user(db,user.email,user.password)
    user_obj = await get_user_by_email(db, user.email)
    if not user_in_db:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_profile = await get_profile_by_user_id(db,user_obj.id)

    return LoginResponse(
        username=user_in_db.username,
        email=user_in_db.email,
        profile={
            "address": user_profile.address,
            "is_admin": user_profile.is_admin,
            "is_girl": user_profile.is_girl,
            "is_verified": user_profile.is_verified,
        }
    )