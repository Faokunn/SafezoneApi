import os
import asyncio
from dotenv import load_dotenv
from typing import Annotated
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import all models for table creation
from models import (
    user_model, profile_model, contacts_model, safezone_model, 
    dangerzone_model, incidentreport_model, sosalerts_model, 
    circle_model, notifications
)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Create the async database engine with connection handling
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_recycle=300,  # Recycle connections every 5 minutes to avoid stale connections
    pool_pre_ping=True  # Ensure connection is active before using it
)

# ✅ Create an async session factory
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# ✅ Dependency for database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session  # Provide session to route
        finally:
            await session.close()  # Ensure session is closed after use

db_dependency = Annotated[AsyncSession, Depends(get_db)]

# ✅ Function to create tables on startup
async def create_tables():
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

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Run table creation at startup
@app.on_event("startup")
async def startup():
    print("Starting up... Creating tables if not exist.")
    await create_tables()

# ✅ Properly close the database engine on shutdown
@app.on_event("shutdown")
async def shutdown():
    print("Shutting down... Closing database connection.")
    await engine.dispose()