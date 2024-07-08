# This module has alreday been converted to ODMantic.

from odmantic import Field, Model, ObjectId
from typing import Optional, List
from pydantic import EmailStr
from pydantic import BaseModel


class UserBase(Model):
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRegister(Model):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserUpdateMe(Model):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UpdatePassword(Model):
    current_password: str
    new_password: str


class User(Model):
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    hashed_password: str
    items: List["Item"] = Field(default_factory=list)


class UserPublic(UserBase):
    public_id: ObjectId


class UsersPublic(Model):
    data: List[UserPublic]
    count: int


class ItemBase(Model):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    title: str


class ItemUpdate(ItemBase):
    title: Optional[str] = None


class Item(Model):
    title: str
    description: Optional[str] = None
    title: str
    owner: Optional[ObjectId] = Field(default=None)
    owner_id: ObjectId


class ItemPublic(Model):
    title: str
    description: Optional[str] = None
    owner_id: ObjectId


class ItemsPublic(BaseModel):
    items: List[ItemPublic]
    count: int


class Message(Model):
    message: str


class Token(Model):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(Model):
    sub: Optional[str] = None


class NewPassword(Model):
    token: str
    new_password: str
