# This module connects to an SQL database.
# Changes are required to switch from SQLModel to ODMantic (MongoDB).

import logging
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from app.core.db import init_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MONGODB_URI = "mongodb+srv://admin:admin1234!@cluster0.ba2wonq.mongodb.net/test-db?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_URI = "db"

# Setup the MongoDB client and engine

client = AsyncIOMotorClient(MONGODB_URI)
engine = AIOEngine(client=client, database="test-db")


async def init() -> None:
    await init_db(engine)


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
