# This module does not establish any SQL database connection.
# No changes required for the switch to ODMantic (MongoDB).

from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings
import logging
from datetime import datetime, timezone

from typing import Union, Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"
logger = logging.getLogger(__name__)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"Token created at {datetime.utcnow()}, expires at {expire}")
    logger.info(f"Subject: {subject}")
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
