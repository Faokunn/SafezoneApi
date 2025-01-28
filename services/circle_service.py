from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.circle_model import Circle
from models.user_model import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import insert
from fastapi import HTTPException, status
from models.association_tables import group_members

async def create_circle(db: AsyncSession, name: str, user_id: int):
    """Create a new circle with the user as the owner."""
    try:
        # Create the circle object
        new_circle = Circle(name=name)
        db.add(new_circle)

        # Commit once to persist the circle in DB
        await db.commit()  # Commit to persist the circle
        await db.refresh(new_circle)  # Refresh to get the circle's ID

        # Fetch the owner (user_id) and associate them as the first member
        owner = await db.get(User, user_id)
        if owner:
            # Insert the owner manually into the association table
            stmt = insert(group_members).values(user_id=user_id, circle_id=new_circle.id)
            await db.execute(stmt)
            await db.commit()  # Commit the changes
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner user not found"
            )

        return new_circle

    except SQLAlchemyError as e:
        await db.rollback()  # Rollback in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating circle: {str(e)}"
        )


async def add_member_to_circle(db: AsyncSession, circle_id: int, user_id: int):
    """Add a user to a circle asynchronously."""
    try:
        # Fetch the circle and user using async context
        circle = await db.get(Circle, circle_id)
        user = await db.get(User, user_id)

        if not circle or not user:
            raise Exception("Circle or user not found.")

        # Check if the user is already a member (optional check)
        query = select(group_members).filter_by(user_id=user_id, circle_id=circle_id)
        result = await db.execute(query)
        if result.scalars().first():
            raise Exception("User is already a member of the circle.")

        # Manually insert a record into the association table
        stmt = insert(group_members).values(user_id=user_id, circle_id=circle_id)
        await db.execute(stmt)

        # Commit the transaction
        await db.commit()

        # Return the updated circle
        return circle

    except SQLAlchemyError as e:
        await db.rollback()  # Rollback in case of error
        raise Exception(f"Error adding member to circle: {str(e)}")




async def get_circle(db: AsyncSession, circle_id: int):
    """Fetch a circle by its ID asynchronously"""
    try:
        stmt = select(Circle).where(Circle.id == circle_id)
        result = await db.execute(stmt)
        circle = result.scalars().first()
        return circle if circle else None
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching circle: {str(e)}")

async def get_all_circles(db: AsyncSession):
    """Fetch all circles asynchronously"""
    try:
        stmt = select(Circle)
        result = await db.execute(stmt)
        circles = result.scalars().all()
        return circles
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching all circles: {str(e)}")

async def remove_member_from_circle(db: AsyncSession, circle_id: int, user_id: int):
    """Remove a user from a circle asynchronously"""
    try:
        circle = await db.get(Circle, circle_id)
        user = await db.get(User, user_id)

        if not circle or not user:
            raise Exception("Circle or user not found.")

        if user in circle.members:
            circle.members.remove(user)
            await db.commit()
            await db.refresh(circle)
            return circle
        else:
            raise Exception("User is not a member of the circle.")
    
    except SQLAlchemyError as e:
        await db.rollback()  # Rollback in case of error
        raise Exception(f"Error removing member from circle: {str(e)}")

async def delete_circle(db: AsyncSession, circle_id: int):
    """Delete a circle by its ID"""
    try:
        circle = await db.get(Circle, circle_id)
        if not circle:
            raise Exception("Circle not found")

        await db.delete(circle)
        await db.commit()
        return circle
    except SQLAlchemyError as e:
        await db.rollback()  # Rollback in case of error
        raise Exception(f"Error deleting circle: {str(e)}")
