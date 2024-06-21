from typing import Any, Union
from odmantic import AIOEngine, Model, query, SyncEngine
from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate


async def create_user(*, engine: AIOEngine, user_create: UserCreate) -> User:
    # Create a User object and hash the password
    db_obj = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password)
    )
    # Save the user to the database
    await engine.save(db_obj)
    return db_obj


async def update_user(*, engine: AIOEngine, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password

    for key, value in {**user_data, **extra_data}.items():
        setattr(db_user, key, value)

    await engine.save(db_user)  # Equivalent to session.add(db_user) and session.commit()
    return db_user


async def get_user_by_email(engine: AIOEngine, email: str) -> Union[User, None]:
    session_user = await engine.find_one(User, User.email == email)
    return session_user


async def authenticate(*, engine: AIOEngine, email: str, password: str) -> Union[User, None]:
    db_user = await get_user_by_email(engine=engine, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


async def create_item(*, engine: AIOEngine, item_in: ItemCreate, owner_id: int) -> Item:
    db_item = Item(**item_in.dict(), owner_id=owner_id)
    await engine.save(db_item)
    return db_item
