# This module connects to a MongoDB database using ODMantic.
# It manages CRUD operations for items ensuring proper user authentication and authorization.

from fastapi import APIRouter, HTTPException, Depends
from odmantic import AIOEngine, ObjectId
from typing import List, Optional
from app.api.deps import get_current_user, get_db
from app.models import (
    Item,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
    Message,
    User,
)

router = APIRouter()


@router.get("/", response_model=ItemsPublic)
async def read_items(
    engine: AIOEngine = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> ItemsPublic:
    """
    Retrieve items accessible by the current user.
    """
    query = {}
    if not current_user.is_superuser:
        query = {"owner_id": current_user.id}

    items = await engine.find(Item, query, skip=skip, limit=limit)
    count = await engine.count(Item, query)

    # Convert database items to ItemPublic objects
    items_public = [ItemPublic(**item.dict()) for item in items]

    return ItemsPublic(items=items_public, count=count)


@router.get("/{item_id}", response_model=ItemPublic)
async def read_item(
    item_id: str,
    engine: AIOEngine = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemPublic:
    """
    Get item by ID.
    """
    item = await engine.find_one(Item, Item.id == ObjectId(item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not enough permissions to access this item"
        )

    return item


@router.post("/", response_model=ItemPublic)
async def create_item(
    item_in: ItemCreate,
    engine: AIOEngine = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemPublic:
    """
    Create a new item.
    """
    item = Item(**item_in.dict(), owner_id=current_user.id)
    await engine.save(item)
    return item


@router.put("/{item_id}", response_model=ItemPublic)
async def update_item(
    item_id: str,
    # item_in: ItemUpdate,
    item_update: ItemUpdate,
    engine: AIOEngine = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemPublic:
    """
    Update an item.
    """
    item = await engine.find_one(Item, Item.id == ObjectId(item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not enough permissions to modify this item"
        )

    # for key, value in item_in.dict(exclude_unset=True).items():
    #     setattr(item, key, value)
    # Remove the _id field from the update data if it exists
    item_update_data = item_update.dict(exclude_unset=True)
    item_update_data.pop("_id", None)

    for key, value in item_update_data.items():
        setattr(item, key, value)

    await engine.save(item)
    return item


@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    engine: AIOEngine = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Message:
    """
    Delete an item.
    """
    item = await engine.find_one(Item, Item.id == ObjectId(item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not enough permissions to delete this item"
        )

    await engine.delete(item)
    return Message(message="Item deleted successfully")
