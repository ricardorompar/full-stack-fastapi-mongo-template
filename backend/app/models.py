# This module has alreday been converted to ODMantic.

from odmantic import Field, Model
from typing import Optional, List
from pydantic import EmailStr

# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(Model):
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserRegister(Model):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: Optional[EmailStr] = None  # type: ignore
    password: Optional[str] = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(Model):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UpdatePassword(Model):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase):
    hashed_password: str
    items: List["Item"] = Field(default_factory=list)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: str


class UsersPublic(Model):
    data: List[UserPublic]
    count: int


# Shared properties
class ItemBase(Model):
    title: str
    description: Optional[str] = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: Optional[str] = None  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase):
    title: str
    owner: Optional[User] = Field(references=User)


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: str
    owner_id: str


class ItemsPublic(ItemBase):
    id: List[ItemPublic]
    count: int


# Generic message
class Message(Model):
    message: str


# JSON payload containing access token
class Token(Model):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(Model):
    sub: Optional[int] = None


class NewPassword(Model):
    token: str
    new_password: str
