# This module connects to an SQL database.
# Changes are required to switch from SQLModel to ODMantic (MongoDB).

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

# from sqlmodel import col, delete, func, select
from odmantic import AIOEngine, ObjectId
from fastapi import APIRouter, Depends, HTTPException, status


from app import crud
from app.api.deps import (
    CurrentUser,
    EngineDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(engine: EngineDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count = await engine.count(User)
    users = await engine.find(User, skip=skip, limit=limit)
    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
async def create_user(*, engine: EngineDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = await crud.get_user_by_email(engine=engine, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = await crud.create_user(engine=engine, user_create=user_in)

    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    *, engine: EngineDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = await crud.get_user_by_email(engine=engine, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    # user_data = user_in.model_dump(exclude_unset=True)
    user_data = user_in.dict(exclude_unset=True)
    # current_user.sqlmodel_update(user_data)

    for key, value in user_data.items():
        setattr(current_user, key, value)

    await engine.save(current_user)
    current_user = await engine.find_one(User, User.id == current_user.id)

    return current_user


@router.patch("/me/password", response_model=Message)
async def update_password_me(
    *, engine: EngineDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    await engine.save(current_user)

    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    try:
        logger.info(f"Current user: {current_user}")
        return current_user
    except Exception as e:
        logger.error(f"Error occurred while fetching current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not fetch current user",
        )
    # return current_user


@router.delete("/me", response_model=Message)
async def delete_user_me(engine: EngineDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    await engine.remove(Item, Item.owner_id == current_user.id)
    await engine.delete(current_user)

    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
async def register_user(engine: EngineDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = await crud.get_user_by_email(engine=engine, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    # user_create = UserCreate.model_validate(user_in)
    # user = await crud.create_user(engine=engine, user_create=user_create)
    # return user
    user_create = UserCreate(**user_in.dict())
    user = User(**user_create.dict())
    await engine.save(user)
    return user


# ... to be continued


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: int, engine: EngineDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = await engine.find_one(User, User.id == ObjectId(user_id))
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    *,
    engine: EngineDep,
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = await engine.find_one(User, User.id == ObjectId(user_id))
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = await crud.get_user_by_email(engine=engine, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = await crud.update_user(engine=engine, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(
    engine: EngineDep, current_user: CurrentUser, user_id: int
) -> Message:
    """
    Delete a user.
    """
    user = await engine.find_one(User, User.id == ObjectId(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    await engine.remove(Item, Item.owner_id == ObjectId(user_id))
    await engine.delete(user)
    return Message(message="User deleted successfully")
