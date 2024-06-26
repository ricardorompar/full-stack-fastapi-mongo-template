# This module does not establish any SQL database connection.
# No changes required for the switch to ODMantic (MongoDB).

from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings
import logging
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"
logger = logging.getLogger(__name__)


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    logger.info(f"Token created at {now}, expires at {expire}")
    logger.info(f"Expires delta: {expires_delta}")
    logger.info(f"Subject: {subject}")
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
