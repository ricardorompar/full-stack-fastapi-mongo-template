# This module connects to an SQL database.
# Changes are required to switch from SQLModel to ODMantic (MongoDB).
# It handles user authentication and authorization, ensuring that only authenticated users
# can access certain resources and that only superusers have certain privileges.
import logging
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from odmantic import AIOEngine, ObjectId

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_db() -> AIOEngine:
    return engine


EngineDep = Annotated[AIOEngine, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(engine: EngineDep, token: TokenDep) -> User:
    payload = None
    logger.info(f"Validating token at {datetime.now(timezone.utc)}")
    try:
        logger.info(f"Token printed : {token}")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        logger.info(f"Decoded payload: {payload}")
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as e:
        logger.error(f"Token validation error: {e}")
        logger.info(f"Decoded payload: {payload}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # new log
    except ValidationError as e:
        logger.error(f"Token validation error: {e}")
        logger.info(f"Decoded payload 2: {payload}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    except jwt.ExpiredSignatureError:
        logger.error("Signature has expired")
        logger.info(f"Decoded payload 3: {payload}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signature has expired",
        )

    user = await engine.find_one(User, User.id == ObjectId(token_data.sub))
    if not user:
        logger.warning(f"User not found: {token_data.sub}")
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        logger.warning(f"Inactive user: {user.id}")
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        logger.warning(f"User does not have superuser privileges: {current_user.id}")
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
