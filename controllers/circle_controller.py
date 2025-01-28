from fastapi import APIRouter, Depends, HTTPException, status, Response
from schemas.circle_schema import CircleSchema, CircleResponse
from services.circle_service import create_circle, get_all_circles, add_member_to_circle, remove_member_from_circle, delete_circle
from database.db_setup import db_dependency
from sqlalchemy.ext.asyncio import AsyncSession
from models.circle_model import Circle
from sqlalchemy import select
from models.association_tables import group_members

router = APIRouter()

# Route to get all circles for a user
@router.get("/get-user-circles/")
async def get_user_circles(user_id: int, db: db_dependency):
    """Get all circles (groups) for a specific user."""
    try:
        # Query circles where the user is a member
        stmt = (
            select(Circle)
            .join(group_members)
            .where(group_members.c.user_id == user_id)
        )
        result = await db.execute(stmt)
        user_circles = result.scalars().all()

        if not user_circles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No circles found for this user"
            )
        
        return user_circles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user circles: {str(e)}"
        )


# Route to create a new circle
@router.post("/create-circle/", response_model=CircleResponse)
async def create_circle_route(circle: CircleSchema, user_id: int, db: db_dependency):
    """Create a new circle with the user as the owner."""
    try:
        new_circle = await create_circle(db, circle.name, user_id)
        return CircleResponse(
            id=new_circle.id,
            name=new_circle.name,
            is_active=new_circle.is_active
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Route to add a member to a circle
@router.post("/add-member-to-circle/")
async def add_member_to_circle_route(circle_id: int, user_id: int, db: db_dependency):
    """Add a member to a circle."""
    try:
        updated_circle = await add_member_to_circle(db, circle_id, user_id)
        return updated_circle
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Route to remove a member from a circle
@router.delete("/remove-member-from-circle/")
async def remove_member_from_circle_route(circle_id: int, user_id: int, db: db_dependency):
    """Remove a member from a circle."""
    try:
        updated_circle = await remove_member_from_circle(db, circle_id, user_id)
        return updated_circle
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Route to delete a circle
@router.delete("/delete-circle/")
async def delete_circle_route(circle_id: int, db: db_dependency):
    """Delete a circle by its ID."""
    try:
        deleted_circle = await delete_circle(db, circle_id)
        if not deleted_circle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
