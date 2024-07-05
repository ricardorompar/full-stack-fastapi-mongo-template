from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# from app.db import engine
from app import crud
from app.core.config import settings
from app.models import User, UserCreate
import logging

client = AsyncIOMotorClient(settings.MONGODB_URI)
engine = AIOEngine(client=client, database=settings.MONGODB_DB)

logger = logging.getLogger(__name__)
async def init_db(engine: AIOEngine) -> None:
    user = await crud.get_user_by_email(engine, settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        created_user = await crud.create_user(engine=engine, user_create=user_in)
        logger.info(
            f"Created first superuser with email: {created_user.email} and _id: {str(created_user.id)}"
        )
    else:
        logger.info(
            f"First superuser already exists: {user.email} with _id: {str(user.id)}"
        )
