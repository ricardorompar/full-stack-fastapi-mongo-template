# This module connects to an SQL database.
# Changes are required to switch from SQLModel to ODMantic (MongoDB).
# This code defines functions to handle user and item management


from typing import Any

# from sqlmodel import Session, select
from odmantic import AIOEngine, Model, query
from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate
from odmantic import SyncEngine
from typing import Union


def create_user(*, engine: SyncEngine, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    engine.save(db_obj)
    db_obj = engine.refresh(db_obj)
    return db_obj


def update_user(*, engine: SyncEngine, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password

    for key, value in {**user_data, **extra_data}.items():
        setattr(db_user, key, value)

    engine.save(db_user)  # Equivalent to session.add(db_user) and session.commit()
    db_user = engine.refresh(db_user)  # Equivalent to session.refresh(db_user)

    return db_user


def get_user_by_email(engine: AIOEngine, email: str) -> User | None:

    session_user = engine.find_one(User, query.eq(User.email, email))
    return session_user


def authenticate(*, engine: SyncEngine, email: str, password: str) -> Union[User, None]:
    db_user = get_user_by_email(engine=engine, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, engine: SyncEngine, item_in: ItemCreate, owner_id: int) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})

    engine.save(db_item)
    db_item = engine.refresh(db_item)
    return db_item
