# This module connects to an SQL database.
# Changes are required to switch from SQLModel to ODMantic (MongoDB).

import logging
from models import UserBase
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 1  # 5 minutes
wait_seconds = 1

client = AsyncIOMotorClient(settings.MONGODB_URI)
engine = AIOEngine(client=client, database=settings.MONGODB_DB)


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init(db_engine: AIOEngine) -> None:
    try:
        # Try to perform a simple operation to check if DB is awake
        c= await client.app.UserBase.find({}).to_list(100)
        print(c)
        await db_engine.find_one(UserBase)  # Assuming `User` is one of your models
    except Exception as e:
        logger.error(e)
        raise e


async def main() -> None:
    logger.info("Initializing service")
    await init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
