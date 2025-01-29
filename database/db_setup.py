import os
import asyncio
import ssl
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

# Create an SSLContext to enforce SSL mode
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False  # Disable hostname verification (if required)

# Create engine with connect_args for SSL configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=None,  # Disable SQLAlchemy connection pooling (Pgbouncer handles it)
    connect_args={
        'ssl': ssl_context  # Pass SSL context here
    }
)

# Create an async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,  # Prevent auto-flushing issues
    autocommit=True  # Required for Pgbouncer in Transaction Mode
)

# Dependency for database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session  # Provide session to route
        finally:
            await session.close()  # Ensure session is closed after use

db_dependency = Annotated[AsyncSession, Depends(get_db)]

# Function to create tables on startup
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

# Initialize FastAPI app
app = FastAPI()

# Run table creation at startup
@app.on_event("startup")
async def startup():
    print("Starting up... Creating tables if not exist.")
    await create_tables()

# Properly close the database engine on shutdown
@app.on_event("shutdown")
async def shutdown():
    print("Shutting down... Closing database connection.")
    try:
        await engine.dispose()
    except Exception as e:
        print(f"Error closing database connection: {e}")
