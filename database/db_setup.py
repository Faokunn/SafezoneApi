from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Annotated
from fastapi import Depends
import os
from dotenv import load_dotenv

from models import user_model,profile_model,contacts_model,safezone_model,dangerzone_model,incidentreport_model,sosalerts_model,circle_model,notifications

#URL_DATABASE = 'postgresql+asyncpg://postgres:admin123!@localhost:5432/safezone'
load_dotenv()
URL_DATABASE = os.getenv("DATABASE_URL")

engine = create_async_engine(URL_DATABASE, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]