import os
import ssl
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends
from typing import Annotated

# Import your models
from models import (
    user_model, profile_model, contacts_model, safezone_model,
    dangerzone_model, incidentreport_model, sosalerts_model,
    circle_model, notifications
)

# Load environment variables
load_dotenv()

# Get the database URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create an SSLContext for secure database connection
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False  # Optional: Disable hostname verification if needed

# Create the async engine with connection management fixes
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={'ssl': ssl_context},  # Pass SSL context here
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_pre_ping=True  # Check connection before using it
)

# Create the async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get the database session in FastAPI routes
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session  # Provide session to route
        finally:
            await session.close()  # Ensure session is closed after use

db_dependency = Annotated[AsyncSession, Depends(get_db)]

# Function to create tables asynchronously
async def create_tables():
    """Create all tables in the database asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(user_model.Base.metadata.create_all)
        await conn.run_sync(profile_model.Base.metadata.create_all)
        await conn.run_sync(contacts_model.Base.metadata.create_all)
        await conn.run_sync(safezone_model.Base.metadata.create_all)
        await conn.run_sync(dangerzone_model.Base.metadata.create_all)
        await conn.run_sync(incidentreport_model.Base.metadata.create_all)
        await conn.run_sync(sosalerts_model.Base.metadata.create_all)
        await conn.run_sync(circle_model.Base.metadata.create_all)
        await conn.run_sync(notifications.Base.metadata.create_all)