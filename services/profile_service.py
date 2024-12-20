from sqlalchemy.future import select
from models.profile_model import Profile

async def get_profile_by_user_id(db, user_id):
    result = await db.execute(select(Profile).filter(Profile.user_id == user_id))
    return result.scalars().first()