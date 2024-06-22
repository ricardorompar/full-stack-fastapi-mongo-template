from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
#from app.db import engine
from app import crud
from app.core.config import settings
from app.models import User, UserCreate

client = AsyncIOMotorClient(settings.MONGODB_URI)
engine = AIOEngine(client=client, database=settings.MONGODB_DB)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-template/issues/28


# Define an asynchronous function to initialize the database
#async def init_db(engine) -> None:
#    # Check if the first superuser already exists
#    user = await crud.get_user_by_email(engine, settings.FIRST_SUPERUSER)
#    if not user:
#        # If the user doesn't exist, create a new UserCreate instance
#        user_in = UserCreate(
#            email=settings.FIRST_SUPERUSER,
#            password=settings.FIRST_SUPERUSER_PASSWORD,
#            is_superuser=True,
#        )
#        # Create the superuser in the database
#        #await crud.create_user(engine, user_create=user_in)
#        await crud.create_user(engine=engine, user_create=user_in)
async def init_db(engine: AIOEngine) -> None:
    user = await crud.get_user_by_email(engine, settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await crud.create_user(engine=engine, user_create=user_in)

# Run the init_db function
#asyncio.run(init_db(engine))